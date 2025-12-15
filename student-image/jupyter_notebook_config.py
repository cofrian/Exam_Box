# Jupyter Notebook Configuration for ExamBox

c = get_config()

# Server settings
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_remote_access = True
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True

# Permitir embedding en iframes
c.ServerApp.tornado_settings = {
    'headers': {
        'Content-Security-Policy': "frame-ancestors 'self' http://localhost:* http://127.0.0.1:*",
        'X-Frame-Options': 'ALLOWALL',
    }
}

# Notebook settings - carpeta raíz de trabajo
c.ServerApp.root_dir = '/home/student/work'

# Security - token is set via environment variable
# c.ServerApp.token = '' # Set via JUPYTER_TOKEN env var

# Disable some features for exam environment
c.ServerApp.terminals_enabled = True
c.LabApp.extensions_in_dev_mode = False

# Autosave
c.ContentsManager.autosave_interval = 60

# Shutdown settings
c.ServerApp.shutdown_no_activity_timeout = 0  # Disabled for exam
