"""
ExamBox - Main FastAPI Application
Exam management system for LAN-based exams with Docker
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from typing import List, Optional
import os
import shutil
import zipfile
import logging

from .database import init_db, get_db
from .models import Exam, StudentSession, Submission
from .schemas import (
    ExamCreate, ExamResponse, StudentRegister, StudentSessionResponse,
    StudentStatus, TimeRemainingResponse, DashboardStudent, DashboardResponse,
    AddTimeRequest, UnlockQuestionRequest, SubmissionResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ExamBox",
    description="Sistema de exámenes en red local con Docker",
    version="1.0.0"
)

# Setup templates and static files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Data paths
DATA_PATH = os.getenv("DATA_PATH", "/app/data")
SUBMISSIONS_PATH = os.path.join(DATA_PATH, "submissions")
WORK_PATH = os.path.join(DATA_PATH, "work")
EXAMS_PATH = os.path.join(DATA_PATH, "exams")
MATERIALS_PATH = os.path.join(DATA_PATH, "materials")


def unlock_question_folder(student_id: str, question_num: int, template_folder: str):
    """Copy a question folder to student's workspace"""
    q_source = os.path.join(EXAMS_PATH, template_folder, f"Q{question_num}")
    q_dest = os.path.join(WORK_PATH, student_id, f"Q{question_num}")
    
    if os.path.exists(q_source) and not os.path.exists(q_dest):
        shutil.copytree(q_source, q_dest)
        logger.info(f"Unlocked Q{question_num} for student {student_id}")


@app.on_event("startup")
async def startup():
    """Initialize database and directories on startup"""
    await init_db()
    
    # Create required directories
    for path in [SUBMISSIONS_PATH, WORK_PATH, EXAMS_PATH, MATERIALS_PATH]:
        os.makedirs(path, exist_ok=True)
    
    logger.info("ExamBox started successfully")


# ============== PROFESSOR UI ROUTES ==============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Professor home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/professor/exams", response_class=HTMLResponse)
async def professor_exams_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Exam management page"""
    result = await db.execute(select(Exam).order_by(Exam.created_at.desc()))
    exams = result.scalars().all()
    return templates.TemplateResponse("professor/exams.html", {
        "request": request,
        "exams": exams
    })


@app.get("/professor/dashboard/{exam_id}", response_class=HTMLResponse)
async def professor_dashboard_page(request: Request, exam_id: int, db: AsyncSession = Depends(get_db)):
    """Dashboard for monitoring exam progress"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    return templates.TemplateResponse("professor/dashboard.html", {
        "request": request,
        "exam": exam
    })


@app.get("/professor/submissions", response_class=HTMLResponse)
async def professor_submissions_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Submissions viewer page"""
    result = await db.execute(select(Exam).order_by(Exam.created_at.desc()))
    exams = result.scalars().all()
    return templates.TemplateResponse("professor/submissions.html", {
        "request": request,
        "exams": exams
    })


# ============== STUDENT UI ROUTES ==============

@app.get("/student", response_class=HTMLResponse)
async def student_login_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Student login page"""
    result = await db.execute(select(Exam).where(Exam.is_active == True))
    exams = result.scalars().all()
    return templates.TemplateResponse("student/login.html", {
        "request": request,
        "exams": exams
    })


@app.get("/student/exam/{session_id}", response_class=HTMLResponse)
async def student_exam_page(request: Request, session_id: int, db: AsyncSession = Depends(get_db)):
    """Student exam interface with timer"""
    session = await db.get(StudentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    exam = await db.get(Exam, session.exam_id)
    
    return templates.TemplateResponse("student/exam_simple.html", {
        "request": request,
        "session": session,
        "exam": exam
    })


# ============== EXAM API ==============

@app.post("/api/exams", response_model=ExamResponse)
async def create_exam(exam: ExamCreate, db: AsyncSession = Depends(get_db)):
    """Create a new exam"""
    db_exam = Exam(**exam.model_dump())
    db.add(db_exam)
    await db.commit()
    await db.refresh(db_exam)
    
    # Create exam template folder if specified
    if exam.template_folder:
        template_path = os.path.join(EXAMS_PATH, exam.template_folder)
        os.makedirs(template_path, exist_ok=True)
        for i in range(1, exam.num_questions + 1):
            os.makedirs(os.path.join(template_path, f"Q{i}"), exist_ok=True)
    
    return db_exam


@app.get("/api/exams", response_model=List[ExamResponse])
async def list_exams(db: AsyncSession = Depends(get_db)):
    """List all exams"""
    result = await db.execute(select(Exam).order_by(Exam.created_at.desc()))
    return result.scalars().all()


@app.get("/api/exams/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Get exam details"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@app.post("/api/exams/{exam_id}/activate")
async def activate_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Activate an exam for students"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam.is_active = True
    await db.commit()
    return {"message": "Exam activated", "exam_id": exam_id}


@app.post("/api/exams/{exam_id}/deactivate")
async def deactivate_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Deactivate an exam"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam.is_active = False
    await db.commit()
    return {"message": "Exam deactivated", "exam_id": exam_id}


# ============== STUDENT SESSION API ==============

@app.post("/api/students/register", response_model=StudentSessionResponse)
async def register_student(student: StudentRegister, db: AsyncSession = Depends(get_db)):
    """Register a student for an exam"""
    # Check exam exists and is active
    exam = await db.get(Exam, student.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if not exam.is_active:
        raise HTTPException(status_code=400, detail="Exam is not active")
    
    # Check if student already registered
    result = await db.execute(
        select(StudentSession).where(
            StudentSession.student_id == student.student_id,
            StudentSession.exam_id == student.exam_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    
    # Create new session
    session = StudentSession(
        student_id=student.student_id,
        student_name=student.student_name,
        exam_id=student.exam_id,
        status="registered"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


@app.post("/api/students/{session_id}/start")
async def start_student_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """Start a student's exam session and create their container"""
    session = await db.get(StudentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    exam = await db.get(Exam, session.exam_id)
    
    # Create workspace directory
    work_dir = os.path.join(WORK_PATH, session.student_id)
    os.makedirs(work_dir, exist_ok=True)
    
    # Copy Q1 to workspace
    if exam.template_folder:
        q1_source = os.path.join(EXAMS_PATH, exam.template_folder, "Q1")
        q1_dest = os.path.join(work_dir, "Q1")
        if os.path.exists(q1_source) and not os.path.exists(q1_dest):
            shutil.copytree(q1_source, q1_dest)
    
    try:
        # Update session (sin Docker dinámico - JupyterLab está siempre corriendo)
        session.status = "in_progress"
        session.started_at = datetime.utcnow()
        session.end_time = datetime.utcnow() + timedelta(minutes=exam.duration_minutes)
        session.jupyter_port = 8888
        session.jupyter_token = "exambox123"
        
        await db.commit()
        await db.refresh(session)
        
        return {
            "session_id": session.id,
            "jupyter_url": f"http://localhost:8888/lab?token=exambox123",
            "end_time": session.end_time.isoformat(),
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start: {str(e)}")


@app.get("/api/students/{session_id}/status", response_model=StudentStatus)
async def get_student_status(session_id: int, db: AsyncSession = Depends(get_db)):
    """Get student session status"""
    session = await db.get(StudentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate remaining time
    time_remaining = 0
    if session.end_time:
        delta = session.end_time - datetime.utcnow()
        time_remaining = max(0, int(delta.total_seconds()))
    
    jupyter_url = None
    if session.jupyter_port and session.jupyter_token:
        jupyter_url = f"http://localhost:{session.jupyter_port}/lab?token={session.jupyter_token}"
    
    return StudentStatus(
        student_id=session.student_id,
        student_name=session.student_name,
        status=session.status,
        current_question=session.current_question,
        unlocked_questions=session.unlocked_questions,
        time_remaining_seconds=time_remaining,
        jupyter_url=jupyter_url
    )


@app.get("/api/students/{session_id}/time", response_model=TimeRemainingResponse)
async def get_time_remaining(session_id: int, db: AsyncSession = Depends(get_db)):
    """Get remaining time for a student"""
    session = await db.get(StudentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    time_remaining = 0
    is_expired = False
    
    if session.end_time:
        delta = session.end_time - datetime.utcnow()
        time_remaining = max(0, int(delta.total_seconds()))
        is_expired = time_remaining == 0
    
    return TimeRemainingResponse(
        student_id=session.student_id,
        time_remaining_seconds=time_remaining,
        end_time=session.end_time,
        is_expired=is_expired
    )


# ============== DASHBOARD API ==============

@app.get("/api/dashboard/{exam_id}", response_model=DashboardResponse)
async def get_dashboard(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Get dashboard data for an exam"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    result = await db.execute(
        select(StudentSession).where(StudentSession.exam_id == exam_id)
    )
    sessions = result.scalars().all()
    
    students = []
    in_progress = 0
    submitted = 0
    
    for session in sessions:
        time_remaining = 0
        if session.end_time:
            delta = session.end_time - datetime.utcnow()
            time_remaining = max(0, int(delta.total_seconds()))
        
        students.append(DashboardStudent(
            id=session.id,
            student_id=session.student_id,
            student_name=session.student_name,
            status=session.status,
            current_question=session.current_question,
            unlocked_questions=session.unlocked_questions,
            time_remaining_seconds=time_remaining,
            jupyter_port=session.jupyter_port
        ))
        
        if session.status == "in_progress":
            in_progress += 1
        elif session.status == "submitted":
            submitted += 1
    
    return DashboardResponse(
        exam=exam,
        students=students,
        total_students=len(students),
        in_progress=in_progress,
        submitted=submitted
    )


# ============== PROFESSOR ACTIONS API ==============

@app.post("/api/actions/add-time")
async def add_time(request: AddTimeRequest, db: AsyncSession = Depends(get_db)):
    """Add extra time to a student"""
    session = await db.get(StudentSession, request.student_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.end_time:
        session.end_time = session.end_time + timedelta(minutes=request.minutes)
        session.extra_minutes += request.minutes
    
    await db.commit()
    return {"message": f"Added {request.minutes} minutes", "new_end_time": session.end_time}


@app.post("/api/actions/unlock-question")
async def unlock_question(request: UnlockQuestionRequest, db: AsyncSession = Depends(get_db)):
    """Unlock next question for a student or all students"""
    exam = await db.get(Exam, request.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    if request.student_session_id:
        # Unlock for specific student
        session = await db.get(StudentSession, request.student_session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.unlocked_questions < exam.num_questions:
            session.unlocked_questions += 1
            
            # Copy question folder to workspace
            if exam.template_folder:
                unlock_question_folder(
                    session.student_id,
                    session.unlocked_questions,
                    exam.template_folder
                )
        
        await db.commit()
        return {"message": f"Unlocked Q{session.unlocked_questions} for {session.student_name}"}
    
    else:
        # Unlock for all students
        result = await db.execute(
            select(StudentSession).where(
                StudentSession.exam_id == request.exam_id,
                StudentSession.status == "in_progress"
            )
        )
        sessions = result.scalars().all()
        
        unlocked_count = 0
        for session in sessions:
            if session.unlocked_questions < exam.num_questions:
                session.unlocked_questions += 1
                unlocked_count += 1
                
                if exam.template_folder:
                    unlock_question_folder(
                        session.student_id,
                        session.unlocked_questions,
                        exam.template_folder
                    )
        
        await db.commit()
        return {"message": f"Unlocked questions for {unlocked_count} students"}


@app.post("/api/actions/force-submit/{session_id}")
async def force_submit(session_id: int, db: AsyncSession = Depends(get_db)):
    """Force submission for a student"""
    session = await db.get(StudentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Trigger submission
    await create_submission(session, db, is_auto=True)
    
    return {"message": f"Forced submission for {session.student_name}"}


# ============== SUBMISSION API ==============

@app.post("/api/submit/{session_id}")
async def submit_exam(session_id: int, db: AsyncSession = Depends(get_db)):
    """Submit exam for a student"""
    session = await db.get(StudentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status == "submitted":
        raise HTTPException(status_code=400, detail="Already submitted")
    
    submission = await create_submission(session, db, is_auto=False)
    
    return {
        "message": "Exam submitted successfully",
        "submission_id": submission.id,
        "file_path": submission.file_path
    }


async def create_submission(session: StudentSession, db: AsyncSession, is_auto: bool = False):
    """Create a submission zip file"""
    exam = await db.get(Exam, session.exam_id)
    
    # Paths
    work_dir = os.path.join(WORK_PATH, session.student_id)
    submission_dir = os.path.join(SUBMISSIONS_PATH, exam.name, session.student_id)
    os.makedirs(submission_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{timestamp}.zip"
    zip_path = os.path.join(submission_dir, zip_filename)
    
    # Create pip freeze file
    freeze_path = os.path.join(work_dir, "pip_freeze.txt")
    try:
        # This would be done inside the container, simplified here
        with open(freeze_path, "w") as f:
            f.write("# Python packages installed\n")
            f.write("# Generated by ExamBox\n")
    except:
        pass
    
    # Create zip
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(work_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, work_dir)
                zipf.write(file_path, arcname)
    
    file_size = os.path.getsize(zip_path)
    
    # Update session
    session.status = "submitted"
    session.submitted_at = datetime.utcnow()
    session.submission_path = zip_path
    
    # Ya no hay contenedores dinámicos, JupyterLab está siempre corriendo
    # El container_id ya no se usa en esta versión simplificada
    
    # Create submission record
    submission = Submission(
        student_session_id=session.id,
        exam_id=session.exam_id,
        student_id=session.student_id,
        file_path=zip_path,
        file_size=file_size,
        is_auto_submit=is_auto
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    return submission


@app.get("/api/submissions/{exam_id}", response_model=List[SubmissionResponse])
async def list_submissions(exam_id: int, db: AsyncSession = Depends(get_db)):
    """List all submissions for an exam"""
    result = await db.execute(
        select(Submission).where(Submission.exam_id == exam_id).order_by(Submission.submitted_at.desc())
    )
    return result.scalars().all()


@app.get("/api/submissions/download/{submission_id}")
async def download_submission(submission_id: int, db: AsyncSession = Depends(get_db)):
    """Download a submission zip file"""
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if not os.path.exists(submission.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        submission.file_path,
        media_type="application/zip",
        filename=os.path.basename(submission.file_path)
    )


# ============== UPLOAD API ==============

@app.post("/api/upload/requirements")
async def upload_requirements(file: UploadFile = File(...)):
    """Upload requirements.txt file"""
    filename = f"requirements_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(DATA_PATH, "requirements", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"filename": filename, "path": filepath}


@app.post("/api/upload/materials/{folder_name}")
async def upload_materials(folder_name: str, files: List[UploadFile] = File(...)):
    """Upload material files"""
    folder_path = os.path.join(MATERIALS_PATH, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    uploaded = []
    for file in files:
        filepath = os.path.join(folder_path, file.filename)
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        uploaded.append(file.filename)
    
    return {"folder": folder_name, "files": uploaded}


# ============== QUESTION MANAGEMENT API ==============

from .models import Question
from .schemas import QuestionCreate, QuestionUpdate, QuestionResponse, ExamWithQuestionsResponse

@app.get("/professor/exam/{exam_id}/editor", response_class=HTMLResponse)
async def exam_editor_page(request: Request, exam_id: int, db: AsyncSession = Depends(get_db)):
    """Editor de preguntas del examen"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    result = await db.execute(
        select(Question).where(Question.exam_id == exam_id).order_by(Question.order)
    )
    questions = result.scalars().all()
    
    return templates.TemplateResponse("professor/exam_editor.html", {
        "request": request,
        "exam": exam,
        "questions": questions
    })


@app.get("/api/exams/{exam_id}/questions", response_model=List[QuestionResponse])
async def get_exam_questions(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener todas las preguntas de un examen"""
    result = await db.execute(
        select(Question).where(Question.exam_id == exam_id).order_by(Question.order)
    )
    return result.scalars().all()


@app.get("/api/exams/{exam_id}/full", response_model=ExamWithQuestionsResponse)
async def get_exam_with_questions(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener examen con todas sus preguntas"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    result = await db.execute(
        select(Question).where(Question.exam_id == exam_id).order_by(Question.order)
    )
    questions = result.scalars().all()
    
    return {
        **exam.__dict__,
        "questions": questions
    }


@app.post("/api/questions", response_model=QuestionResponse)
async def create_question(question: QuestionCreate, db: AsyncSession = Depends(get_db)):
    """Crear una nueva pregunta"""
    # Verificar que el examen existe
    exam = await db.get(Exam, question.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    db_question = Question(**question.model_dump())
    db.add(db_question)
    
    # Actualizar el número de preguntas del examen
    result = await db.execute(
        select(Question).where(Question.exam_id == question.exam_id)
    )
    count = len(result.scalars().all()) + 1
    exam.num_questions = count
    
    await db.commit()
    await db.refresh(db_question)
    
    # Crear carpeta de pregunta
    question_folder = os.path.join(EXAMS_PATH, f"exam_{question.exam_id}", f"Q{question.order}")
    os.makedirs(question_folder, exist_ok=True)
    
    return db_question


@app.put("/api/questions/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question_data: QuestionUpdate, db: AsyncSession = Depends(get_db)):
    """Actualizar una pregunta"""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    update_data = question_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    
    await db.commit()
    await db.refresh(question)
    return question


@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    """Eliminar una pregunta"""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    exam_id = question.exam_id
    await db.delete(question)
    
    # Reordenar preguntas restantes
    result = await db.execute(
        select(Question).where(Question.exam_id == exam_id).order_by(Question.order)
    )
    remaining = result.scalars().all()
    for i, q in enumerate(remaining, 1):
        q.order = i
    
    # Actualizar número de preguntas del examen
    exam = await db.get(Exam, exam_id)
    exam.num_questions = len(remaining)
    
    await db.commit()
    return {"message": "Question deleted"}


@app.post("/api/questions/{question_id}/upload")
async def upload_question_file(
    question_id: int, 
    file: UploadFile = File(...),
    file_type: str = Form("file"),  # "file", "pdf", "csv", "image"
    db: AsyncSession = Depends(get_db)
):
    """Subir archivo adjunto a una pregunta"""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Determinar carpeta de destino
    question_folder = os.path.join(EXAMS_PATH, f"exam_{question.exam_id}", f"Q{question.order}")
    os.makedirs(question_folder, exist_ok=True)
    
    # Guardar archivo
    filepath = os.path.join(question_folder, file.filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    file_size = os.path.getsize(filepath)
    
    # Si es PDF, actualizar el campo pdf_file
    if file_type == "pdf" or file.filename.lower().endswith('.pdf'):
        question.pdf_file = filepath
    else:
        # Agregar a attachments
        attachments = question.attachments or []
        attachments.append({
            "name": file.filename,
            "path": filepath,
            "type": file_type,
            "size": file_size
        })
        question.attachments = attachments
    
    await db.commit()
    await db.refresh(question)
    
    return {
        "message": "File uploaded",
        "filename": file.filename,
        "path": filepath,
        "size": file_size
    }


@app.delete("/api/questions/{question_id}/files/{filename}")
async def delete_question_file(question_id: int, filename: str, db: AsyncSession = Depends(get_db)):
    """Eliminar archivo adjunto de una pregunta"""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question_folder = os.path.join(EXAMS_PATH, f"exam_{question.exam_id}", f"Q{question.order}")
    filepath = os.path.join(question_folder, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Actualizar attachments
    if question.attachments:
        question.attachments = [a for a in question.attachments if a["name"] != filename]
    
    # Limpiar pdf_file si corresponde
    if question.pdf_file and filename in question.pdf_file:
        question.pdf_file = None
    
    await db.commit()
    return {"message": "File deleted"}


@app.post("/api/questions/{question_id}/generate-notebook")
async def generate_question_notebook(question_id: int, db: AsyncSession = Depends(get_db)):
    """Generar notebook de pregunta basado en el contenido"""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Crear estructura del notebook
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {question.title}\n\n{question.description or ''}"]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    # Agregar celda de instrucciones si existe
    if question.instructions:
        notebook["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"## Instrucciones\n\n{question.instructions}"]
        })
    
    # Agregar celda de código inicial
    if question.starter_code:
        notebook["cells"].append({
            "cell_type": "code",
            "metadata": {},
            "source": [question.starter_code],
            "execution_count": None,
            "outputs": []
        })
    else:
        notebook["cells"].append({
            "cell_type": "code",
            "metadata": {},
            "source": ["# Tu código aquí\n"],
            "execution_count": None,
            "outputs": []
        })
    
    # Guardar notebook
    import json
    question_folder = os.path.join(EXAMS_PATH, f"exam_{question.exam_id}", f"Q{question.order}")
    os.makedirs(question_folder, exist_ok=True)
    notebook_path = os.path.join(question_folder, f"pregunta{question.order}.ipynb")
    
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    return {
        "message": "Notebook generated",
        "path": notebook_path
    }


@app.get("/api/files/{exam_id}/{question_order}/{filename}")
async def serve_question_file(exam_id: int, question_order: int, filename: str):
    """Servir archivo de pregunta (para PDFs, CSVs, etc.)"""
    filepath = os.path.join(EXAMS_PATH, f"exam_{exam_id}", f"Q{question_order}", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(filepath)


# ============== HEALTH CHECK ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
