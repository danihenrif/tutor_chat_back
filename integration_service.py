import json

def unify_student_data(course_structure, student_specific_data):
    """
    Funde a estrutura global do curso com o progresso específico de um aluno.
    
    Args:
        course_structure (dict): O JSON estático com modules -> lessons -> video_url e course_id.
        student_specific_data (dict): O JSON do aluno específico com lessons -> status ('visto').
    
    Returns:
        dict: Dicionário (dict) no formato StudentData pronto para o Flutter.
    """
    
    viewed_lessons_ids = set()
    if student_specific_data and 'lessons' in student_specific_data:
        for lesson in student_specific_data.get('lessons', []):
            if lesson.get('status') == 'visto':
                viewed_lessons_ids.add(lesson.get('lesson_id'))

    final_modules = []

    if course_structure and 'modules' in course_structure:
        for module in course_structure.get('modules', []):
            module_title = module.get('title')
            module_id = module.get('module_id') 
            
            formatted_lessons = []

            for lesson in module.get('lessons', []):
                lesson_id = lesson.get('lesson_id')
                
                view_status = 1 if lesson_id in viewed_lessons_ids else 0

                formatted_lessons.append({
                    "lesson_name": lesson.get('title'),
                    "video_link": lesson.get('video_url'),
                    "view_status": view_status,
                    "lesson_id": lesson_id
                })

            final_modules.append({
                "module_name": module_title,
                "module_id": module_id, 
                "lessons": formatted_lessons
            })

    student_id = student_specific_data.get('student_id') if student_specific_data else "unknown"
    
    course_id = course_structure.get('course_id') if course_structure else None

    final_data = {
        "student_id": student_id,
        "course_id": course_id,
        "modules": final_modules
    }
    
    return final_data