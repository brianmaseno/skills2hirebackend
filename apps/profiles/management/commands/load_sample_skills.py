"""
Django management command to load sample skills
"""
from django.core.management.base import BaseCommand
from apps.profiles.models import Skill


class Command(BaseCommand):
    help = 'Load sample skills into the database'

    def handle(self, *args, **kwargs):
        skills_data = [
            # Programming Languages
            {'name': 'Python', 'category': 'Programming Languages'},
            {'name': 'JavaScript', 'category': 'Programming Languages'},
            {'name': 'Java', 'category': 'Programming Languages'},
            {'name': 'C++', 'category': 'Programming Languages'},
            {'name': 'C#', 'category': 'Programming Languages'},
            {'name': 'PHP', 'category': 'Programming Languages'},
            {'name': 'Ruby', 'category': 'Programming Languages'},
            {'name': 'Go', 'category': 'Programming Languages'},
            {'name': 'Rust', 'category': 'Programming Languages'},
            {'name': 'TypeScript', 'category': 'Programming Languages'},
            
            # Web Frameworks
            {'name': 'Django', 'category': 'Web Frameworks'},
            {'name': 'Flask', 'category': 'Web Frameworks'},
            {'name': 'React', 'category': 'Web Frameworks'},
            {'name': 'Angular', 'category': 'Web Frameworks'},
            {'name': 'Vue.js', 'category': 'Web Frameworks'},
            {'name': 'Node.js', 'category': 'Web Frameworks'},
            {'name': 'Express.js', 'category': 'Web Frameworks'},
            {'name': 'Next.js', 'category': 'Web Frameworks'},
            {'name': 'Laravel', 'category': 'Web Frameworks'},
            {'name': 'Ruby on Rails', 'category': 'Web Frameworks'},
            
            # Databases
            {'name': 'PostgreSQL', 'category': 'Databases'},
            {'name': 'MySQL', 'category': 'Databases'},
            {'name': 'MongoDB', 'category': 'Databases'},
            {'name': 'Redis', 'category': 'Databases'},
            {'name': 'Elasticsearch', 'category': 'Databases'},
            {'name': 'SQLite', 'category': 'Databases'},
            {'name': 'Oracle', 'category': 'Databases'},
            {'name': 'Microsoft SQL Server', 'category': 'Databases'},
            
            # Cloud & DevOps
            {'name': 'AWS', 'category': 'Cloud & DevOps'},
            {'name': 'Azure', 'category': 'Cloud & DevOps'},
            {'name': 'Google Cloud Platform', 'category': 'Cloud & DevOps'},
            {'name': 'Docker', 'category': 'Cloud & DevOps'},
            {'name': 'Kubernetes', 'category': 'Cloud & DevOps'},
            {'name': 'Jenkins', 'category': 'Cloud & DevOps'},
            {'name': 'Git', 'category': 'Cloud & DevOps'},
            {'name': 'CI/CD', 'category': 'Cloud & DevOps'},
            {'name': 'Terraform', 'category': 'Cloud & DevOps'},
            {'name': 'Ansible', 'category': 'Cloud & DevOps'},
            
            # Data Science & ML
            {'name': 'Machine Learning', 'category': 'Data Science & ML'},
            {'name': 'Deep Learning', 'category': 'Data Science & ML'},
            {'name': 'TensorFlow', 'category': 'Data Science & ML'},
            {'name': 'PyTorch', 'category': 'Data Science & ML'},
            {'name': 'Pandas', 'category': 'Data Science & ML'},
            {'name': 'NumPy', 'category': 'Data Science & ML'},
            {'name': 'Scikit-learn', 'category': 'Data Science & ML'},
            {'name': 'Data Analysis', 'category': 'Data Science & ML'},
            {'name': 'Data Visualization', 'category': 'Data Science & ML'},
            
            # Mobile Development
            {'name': 'React Native', 'category': 'Mobile Development'},
            {'name': 'Flutter', 'category': 'Mobile Development'},
            {'name': 'iOS Development', 'category': 'Mobile Development'},
            {'name': 'Android Development', 'category': 'Mobile Development'},
            {'name': 'Swift', 'category': 'Mobile Development'},
            {'name': 'Kotlin', 'category': 'Mobile Development'},
            
            # Soft Skills
            {'name': 'Communication', 'category': 'Soft Skills'},
            {'name': 'Leadership', 'category': 'Soft Skills'},
            {'name': 'Problem Solving', 'category': 'Soft Skills'},
            {'name': 'Team Collaboration', 'category': 'Soft Skills'},
            {'name': 'Project Management', 'category': 'Soft Skills'},
            {'name': 'Agile/Scrum', 'category': 'Soft Skills'},
        ]

        created_count = 0
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={'category': skill_data['category']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created skill: {skill.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully loaded {created_count} new skills '
                f'({len(skills_data) - created_count} already existed)'
            )
        )
