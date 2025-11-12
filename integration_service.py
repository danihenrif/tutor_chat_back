import json

def process_course_content(course_data):
    formatted_course_links = {}
    for module in course_data.get('modulos', []):
        module_name = module['nome_modulo']
        if module_name not in formatted_course_links:
            formatted_course_links[module_name] = {}
        
        for lesson in module.get('aulas', []):
            lesson_name = lesson['nome_aula']
            video_link = lesson['link_video']
            formatted_course_links[module_name][lesson_name] = {'video_link': video_link}

    return formatted_course_links

def process_student_progress(progress_data, course_links):
    student_id = progress_data.get('aluno_id')
    final_modules_data = {}
    
    for progress_module in progress_data.get('modulos', []):
        module_name = progress_module['nome_modulo']
        lessons_list = []
        
        if module_name in course_links:
            for progress_lesson in progress_module.get('aulas', []):
                lesson_name = progress_lesson['nome_aula']
                view_status = progress_lesson['visto']
                
                link_details = course_links[module_name].get(lesson_name, {})
                video_link = link_details.get('video_link', 'Link indisponível')
                
                lessons_list.append({
                    'lesson_name': lesson_name, 
                    'video_link': video_link, 
                    'view_status': view_status
                })
        
            final_modules_data[module_name] = {'lessons': lessons_list}

    return {'student_id': student_id, 'modules': final_modules_data}


def unify_and_send(course_data, progress_data):
    course_links = process_course_content(course_data)
    
    final_data = process_student_progress(progress_data, course_links)
    
    
    modules_list = []
    for module_name, module_details in final_data['modules'].items():
        lessons_list = module_details['lessons']
        
        modules_list.append({
            'module_name': module_name, 
            'lessons': lessons_list
        })

    final_json = {
        'student_id': final_data['student_id'],
        'modules': modules_list
    }
    
    return json.dumps(final_json)