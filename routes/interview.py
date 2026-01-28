
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from extensions import db
from models.user import User
from models.resume import Resume
from models.interview import Interview
from models.interview_question import InterviewQuestion
from services.interview_engine import InterviewEngine
from services.interview_evaluator import InterviewEvaluator

interview_bp = Blueprint("interview", __name__)

# ========================================
# START INTERVIEW SESSION
# ========================================
@interview_bp.route("/start", methods=["POST"])
@jwt_required()
def start_interview():
    """
    Start a new interview session
    Body: {
        "resume_id": 1,
        "interview_type": "hr",  # hr, technical, ai_mock
        "language": "python"  # optional, for technical interviews
    }
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check interview limits
    if not user.can_take_interview():
        return jsonify({
            "error": "Interview limit reached",
            "message": f"Free tier allows {user.max_interviews} interviews. Upgrade to Pro for unlimited.",
            "current_count": user.interview_count,
            "max_interviews": user.max_interviews,
            "upgrade_required": True
        }), 403
    
    data = request.json
    resume_id = data.get('resume_id')
    interview_type = data.get('interview_type', 'hr')
    language = data.get('language')
    
    # Validate resume exists and belongs to user
    resume = None
    if resume_id:
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user_id).first()
        if not resume:
            return jsonify({"error": "Resume not found"}), 404
    
    try:
        # Create interview record
        interview = Interview(
            user_id=current_user_id,
            resume_id=resume_id,
            interview_type=interview_type,
            language=language,
            status='in_progress',
            started_at=datetime.utcnow()
        )
        
        db.session.add(interview)
        db.session.commit()
        
        # Generate questions using AI
        engine = InterviewEngine()
        questions = engine.generate_questions(
            interview_type=interview_type,
            resume_data=resume.to_dict() if resume else None,
            language=language
        )
        
        # Store questions in database
        for idx, q_text in enumerate(questions):
            question = InterviewQuestion(
                interview_id=interview.id,
                question_text=q_text,
                question_type=interview_type,
                question_order=idx + 1
            )
            db.session.add(question)
        
        interview.total_questions = len(questions)
        db.session.commit()
        
        # Get first question
        first_question = InterviewQuestion.query.filter_by(
            interview_id=interview.id,
            question_order=1
        ).first()
        
        return jsonify({
            "message": "Interview started successfully",
            "interview_id": interview.id,
            "interview_type": interview_type,
            "total_questions": len(questions),
            "first_question": {
                "id": first_question.id,
                "text": first_question.question_text,
                "order": 1
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to start interview: {str(e)}"}), 500

# ========================================
# SUBMIT ANSWER
# ========================================
@interview_bp.route("/answer", methods=["POST"])
@jwt_required()
def submit_answer():
    """
    Submit answer to a question
    Body: {
        "question_id": 1,
        "answer": "In my previous role at...",
        "time_taken": 120  # seconds
    }
    """
    current_user_id = get_jwt_identity()
    
    data = request.json
    question_id = data.get('question_id')
    answer_text = data.get('answer', '').strip()
    time_taken = data.get('time_taken', 0)
    
    if not question_id or not answer_text:
        return jsonify({"error": "Question ID and answer required"}), 400
    
    # Get question and verify ownership
    question = InterviewQuestion.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    interview = Interview.query.get(question.interview_id)
    if interview.user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    if question.candidate_answer:
        return jsonify({"error": "Question already answered"}), 400
    
    try:
        # Evaluate answer using AI
        evaluator = InterviewEvaluator()
        evaluation = evaluator.evaluate_answer(
            question_text=question.question_text,
            answer_text=answer_text,
            interview_type=interview.interview_type
        )
        
        # Update question record
        question.candidate_answer = answer_text
        question.time_taken_seconds = time_taken
        question.score = evaluation['score']
        question.ai_evaluation = evaluation
        question.answered_at = datetime.utcnow()
        
        # Update interview progress
        interview.questions_answered += 1
        
        db.session.commit()
        
        # Get next question
        next_question = InterviewQuestion.query.filter_by(
            interview_id=interview.id,
            candidate_answer=None
        ).order_by(InterviewQuestion.question_order).first()
        
        if next_question:
            # More questions remaining
            return jsonify({
                "message": "Answer submitted",
                "evaluation": evaluation,
                "progress": {
                    "answered": interview.questions_answered,
                    "total": interview.total_questions
                },
                "next_question": {
                    "id": next_question.id,
                    "text": next_question.question_text,
                    "order": next_question.question_order
                }
            }), 200
        else:
            # Interview complete
            return complete_interview(interview.id)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to submit answer: {str(e)}"}), 500

# ========================================
# COMPLETE INTERVIEW (Internal Helper)
# ========================================
def complete_interview(interview_id):
    """
    Calculate final scores and complete interview
    """
    interview = Interview.query.get(interview_id)
    
    # Get all answered questions
    questions = InterviewQuestion.query.filter_by(interview_id=interview_id).all()
    
    if not questions:
        return jsonify({"error": "No questions found"}), 400
    
    # Calculate scores
    total_score = sum(q.score for q in questions if q.score) / len(questions)
    
    # Calculate component scores (if AI provides them)
    technical_scores = []
    communication_scores = []
    star_scores = []
    
    for q in questions:
        if q.ai_evaluation:
            eval_data = q.ai_evaluation
            technical_scores.append(eval_data.get('technical_score', total_score))
            communication_scores.append(eval_data.get('communication_score', total_score))
            
            star = eval_data.get('star_components', {})
            star_score = sum([
                25 if star.get('situation') else 0,
                25 if star.get('task') else 0,
                25 if star.get('action') else 0,
                25 if star.get('result') else 0
            ])
            star_scores.append(star_score)
    
    # Update interview record
    interview.overall_score = round(total_score)
    interview.technical_score = round(sum(technical_scores) / len(technical_scores)) if technical_scores else None
    interview.communication_score = round(sum(communication_scores) / len(communication_scores)) if communication_scores else None
    interview.star_method_score = round(sum(star_scores) / len(star_scores)) if star_scores else None
    interview.status = 'completed'
    interview.completed_at = datetime.utcnow()
    
    # Calculate duration
    if interview.started_at:
        duration = (interview.completed_at - interview.started_at).total_seconds()
        interview.duration_seconds = int(duration)
    
    # Generate overall AI feedback
    evaluator = InterviewEvaluator()
    overall_feedback = evaluator.generate_overall_feedback(questions, interview.overall_score)
    interview.ai_feedback = overall_feedback
    
    # Increment user's interview count
    user = User.query.get(interview.user_id)
    user.increment_interview_count()
    
    db.session.commit()
    
    return jsonify({
        "message": "Interview completed",
        "status": "completed",
        "overall_score": interview.overall_score,
        "readiness_status": interview.get_readiness_status(),
        "breakdown": {
            "technical": interview.technical_score,
            "communication": interview.communication_score,
            "star_method": interview.star_method_score
        },
        "duration_seconds": interview.duration_seconds,
        "ai_feedback": overall_feedback,
        "redirect_url": f"/interview/{interview.id}/review"
    }), 200

# ========================================
# GET INTERVIEW REVIEW
# ========================================
@interview_bp.route("/<int:interview_id>/review", methods=["GET"])
@jwt_required()
def get_interview_review(interview_id):
    """
    Get detailed review of completed interview
    """
    current_user_id = get_jwt_identity()
    
    interview = Interview.query.filter_by(id=interview_id, user_id=current_user_id).first()
    
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    
    if interview.status != 'completed':
        return jsonify({"error": "Interview not completed yet"}), 400
    
    # Get all questions with answers and evaluations
    questions = InterviewQuestion.query.filter_by(interview_id=interview_id).order_by(
        InterviewQuestion.question_order
    ).all()
    
    return jsonify({
        "interview": interview.to_dict(),
        "questions": [q.to_dict() for q in questions],
        "summary": {
            "total_questions": interview.total_questions,
            "overall_score": interview.overall_score,
            "readiness_status": interview.get_readiness_status(),
            "color": interview.get_score_color(),
            "duration_minutes": round(interview.duration_seconds / 60) if interview.duration_seconds else None
        }
    }), 200

# ========================================
# GET USER'S INTERVIEW HISTORY
# ========================================
@interview_bp.route("/history", methods=["GET"])
@jwt_required()
def get_interview_history():
    """
    Get all interviews for current user
    """
    current_user_id = get_jwt_identity()
    
    interviews = Interview.query.filter_by(user_id=current_user_id).order_by(
        Interview.created_at.desc()
    ).all()
    
    return jsonify({
        "interviews": [i.to_dict() for i in interviews],
        "count": len(interviews)
    }), 200

# ========================================
# DELETE INTERVIEW
# ========================================
@interview_bp.route("/<int:interview_id>", methods=["DELETE"])
@jwt_required()
def delete_interview(interview_id):
    """
    Delete interview and all associated data
    """
    current_user_id = get_jwt_identity()
    
    interview = Interview.query.filter_by(id=interview_id, user_id=current_user_id).first()
    
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    
    db.session.delete(interview)
    db.session.commit()
    
    return jsonify({"message": "Interview deleted successfully"}), 200

# ========================================
# RETRY SPECIFIC QUESTION
# ========================================
@interview_bp.route("/retry-question/<int:question_id>", methods=["POST"])
@jwt_required()
def retry_question(question_id):
    """
    Allow user to retry answering a specific question
    Body: {
        "answer": "new answer text"
    }
    """
    current_user_id = get_jwt_identity()
    
    question = InterviewQuestion.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    interview = Interview.query.get(question.interview_id)
    if interview.user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    new_answer = data.get('answer', '').strip()
    
    if not new_answer:
        return jsonify({"error": "Answer required"}), 400
    
    try:
        # Re-evaluate with new answer
        evaluator = InterviewEvaluator()
        evaluation = evaluator.evaluate_answer(
            question_text=question.question_text,
            answer_text=new_answer,
            interview_type=interview.interview_type
        )
        
        # Update question
        question.candidate_answer = new_answer
        question.score = evaluation['score']
        question.ai_evaluation = evaluation
        question.answered_at = datetime.utcnow()
        
        # Recalculate interview overall score
        all_questions = InterviewQuestion.query.filter_by(interview_id=interview.id).all()
        new_avg = sum(q.score for q in all_questions if q.score) / len(all_questions)
        interview.overall_score = round(new_avg)
        
        db.session.commit()
        
        return jsonify({
            "message": "Answer updated",
            "new_score": evaluation['score'],
            "evaluation": evaluation,
            "interview_overall_score": interview.overall_score
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to retry: {str(e)}"}), 500
