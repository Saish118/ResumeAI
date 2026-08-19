"""ResumeAI Controlled Skill Taxonomy and Alias Definitions."""

from typing import Dict, List, TypedDict


class SkillEntry(TypedDict):
    category: str
    aliases: List[str]


SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Programming Languages": {
        "Python": ["python", "python 3", "python3", "py"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "TypeScript": ["typescript", "ts"],
        "Java": ["java"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "c sharp", "csharp"],
        ".NET": [".net", "dotnet", "dot net"],
        "Go": ["golang", "go programming", "go lang"],
        "Rust": ["rust", "rustlang"],
        "Ruby": ["ruby"],
        "PHP": ["php"],
        "Swift": ["swift"],
        "Kotlin": ["kotlin"],
        "R": ["r language", "r programming"],
    },
    "Web Development": {
        "React": ["react", "react.js", "reactjs", "react js"],
        "Angular": ["angular", "angular.js", "angularjs"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Node.js": ["node.js", "nodejs", "node js"],
        "Express.js": ["express", "express.js", "expressjs"],
        "Next.js": ["next.js", "nextjs", "next js"],
        "FastAPI": ["fastapi", "fast api"],
        "Django": ["django"],
        "Flask": ["flask"],
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
        "REST API": ["rest api", "restful api", "rest apis", "restful apis"],
        "GraphQL": ["graphql"],
    },
    "Databases": {
        "PostgreSQL": ["postgres", "postgresql", "psql", "postgres database"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite", "sqlite3"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
        "Cassandra": ["cassandra", "apache cassandra"],
        "Oracle": ["oracle", "oracle db"],
        "SQL": ["sql"],
    },
    "Machine Learning / AI": {
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "dl"],
        "PyTorch": ["pytorch", "torch"],
        "TensorFlow": ["tensorflow", "tf"],
        "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
        "Keras": ["keras"],
        "Natural Language Processing": ["nlp", "natural language processing"],
        "Computer Vision": ["cv", "computer vision"],
        "OpenCV": ["opencv"],
        "LLMs": ["llm", "llms", "large language models"],
    },
    "Data": {
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "SciPy": ["scipy"],
        "Apache Spark": ["spark", "apache spark", "pyspark"],
        "Data Analysis": ["data analysis", "data analytics"],
        "Data Engineering": ["data engineering", "data pipeline", "data pipelines"],
    },
    "DevOps / Cloud": {
        "Docker": ["docker", "docker container", "docker containers"],
        "Kubernetes": ["k8s", "kubernetes"],
        "AWS": ["aws", "amazon web services"],
        "GCP": ["gcp", "google cloud", "google cloud platform"],
        "Azure": ["azure", "microsoft azure"],
        "CI/CD": ["ci/cd", "ci-cd", "continuous integration"],
        "Terraform": ["terraform"],
        "Nginx": ["nginx"],
    },
    "Tools / Version Control": {
        "Git": ["git"],
        "GitHub": ["github"],
        "GitLab": ["gitlab"],
        "Linux": ["linux", "unix"],
        "Jira": ["jira"],
    },
}
