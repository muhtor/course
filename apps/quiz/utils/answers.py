from ...quiz.models import QuizTaker, UsersAnswer


def get_user_correct_answers_count(quiz_taker: QuizTaker):
    correct_answers_count = 0
    for user_answer in quiz_taker.answers.prefetch_related('answers'):
        # Check for valid of every Answer in UserAnswer
        is_correct = True
        selected_answers = user_answer.answers.all()
        for answer in selected_answers:
            if not answer.is_correct:
                is_correct = False
                break

        if is_correct and selected_answers.count() > 0:
            correct_answers_count += 1
    return correct_answers_count
