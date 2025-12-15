"""
SQLAlchemy models for ExamBox
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    subject = Column(String(200), nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    num_questions = Column(Integer, nullable=False, default=3)
    profile = Column(String(50), default="jupyter")  # "jupyter" or "desktop"
    requirements_file = Column(String(500), nullable=True)
    materials_folder = Column(String(500), nullable=True)
    template_folder = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    students = relationship("StudentSession", back_populates="exam")
    questions = relationship("Question", back_populates="exam", order_by="Question.order")


class Question(Base):
    """Modelo para preguntas individuales del examen"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    order = Column(Integer, nullable=False, default=1)  # Q1, Q2, Q3...
    
    # Contenido
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)  # Markdown/HTML
    instructions = Column(Text, nullable=True)  # Instrucciones detalladas
    starter_code = Column(Text, nullable=True)  # Código inicial para el notebook
    
    # Archivos adjuntos
    attachments = Column(JSON, default=list)  # Lista de archivos: [{"name": "data.csv", "path": "..."}]
    pdf_file = Column(String(500), nullable=True)  # PDF de la pregunta
    
    # Puntuación
    points = Column(Integer, default=10)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exam = relationship("Exam", back_populates="questions")


class StudentSession(Base):
    __tablename__ = "student_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    student_name = Column(String(200), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    
    # Session state
    status = Column(String(50), default="registered")  # registered, in_progress, submitted
    container_id = Column(String(100), nullable=True)
    jupyter_port = Column(Integer, nullable=True)
    jupyter_token = Column(String(100), nullable=True)
    
    # Progress tracking
    current_question = Column(Integer, default=1)
    unlocked_questions = Column(Integer, default=1)
    
    # Time tracking
    started_at = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    extra_minutes = Column(Integer, default=0)
    
    # Submission
    submitted_at = Column(DateTime, nullable=True)
    submission_path = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exam = relationship("Exam", back_populates="students")


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_session_id = Column(Integer, ForeignKey("student_sessions.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    is_auto_submit = Column(Boolean, default=False)
