# RASBERRY PIE
ssh -6 isiri@isiri.local\
after password\
python3 rpi_gpio_service.py --port 5000

# BACKEND
uvicorn backend.app.main:app --reload

# FRONTNED
cd frontend\
npm run dev