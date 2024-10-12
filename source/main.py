from BEE import BEE

app = Back()

@app.route('/')
def home(): return "Welcome to Back!"

@app.route('/about')
def about(): return "About Back"
