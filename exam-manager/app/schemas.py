"""
Pydantic schemas for API validation
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Exam schemas
class ExamCreate(BaseModel):
    name: str
    subject: str
    duration_minutes: int = 60
    num_questions: int = 3
    profile: str = "jupyter"
    requirements_file: Optional[str] = None
    materials_folder: Optional[str] = None
    template_folder: Optional[str] = None


class ExamResponse(BaseModel):
    id: int
    name: str
    subject: str
    duration_minutes: int
    num_questions: int
    profile: str
    requirements_file: Optional[str]
    materials_folder: Optional[str]
    template_folder: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Student schemas
class StudentRegister(BaseModel):
    student_id: str
    student_name: str
    exam_id: int


class StudentSessionResponse(BaseModel):
    id: int
    student_id: str
    student_name: str
    exam_id: int
    status: str
    jupyter_port: Optional[int]
    jupyter_token: Optional[str]
    current_question: int
    unlocked_questions: int
    started_at: Optional[datetime]
    end_time: Optional[datetime]
    extra_minutes: int
    submitted_at: Optional[datetime]

    class Config:
        from_attributes = True


class StudentStatus(BaseModel):
    student_id: str
    student_name: str
    status: str
    current_question: int
    unlocked_questions: int
    time_remaining_seconds: int
    jupyter_url: Optional[str]


class TimeRemainingResponse(BaseModel):
    student_id: str
    time_remaining_seconds: int
    end_time: Optional[datetime]
    is_expired: bool


# Dashboard schemas
class DashboardStudent(BaseModel):
    id: int
    student_id: str
    student_name: str
    status: str
    current_question: int
    unlocked_questions: int
    time_remaining_seconds: int
    jupyter_port: Optional[int]


class DashboardResponse(BaseModel):
    exam: ExamResponse
    students: List[DashboardStudent]
    total_students: int
    in_progress: int
    submitted: int


# Action schemas
class AddTimeRequest(BaseModel):
    student_session_id: int
    minutes: int = 5


class UnlockQuestionRequest(BaseModel):
    student_session_id: Optional[int] = None  # None = all students
    exam_id: int


class SubmissionResponse(BaseModel):
    id: int
    student_id: str
    file_path: str
    file_size: Optional[int]
    submitted_at: datetime
    is_auto_submit: bool

    class Config:
        from_attributes = True


# Question schemas
class AttachmentInfo(BaseModel):
    name: str
    path: str
    type: str = "file"  # "file", "pdf", "csv", "image"
    size: Optional[int] = None


class QuestionCreate(BaseModel):
    exam_id: int
    order: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    starter_code: Optional[str] = None
    points: int = 10


class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    starter_code: Optional[str] = None
    points: Optional[int] = None
    order: Optional[int] = None


class QuestionResponse(BaseModel):
    id: int
    exam_id: int
    order: int
    title: str
    description: Optional[str]
    instructions: Optional[str]
    starter_code: Optional[str]
    attachments: List[AttachmentInfo] = []
    pdf_file: Optional[str]
    points: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExamWithQuestionsResponse(BaseModel):
    id: int
    name: str
    subject: str
    duration_minutes: int
    num_questions: int
    profile: str
    is_active: bool
    created_at: datetime
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True
