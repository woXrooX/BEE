from BEE.BEE import BEE

app = BEE()

@app.route('/')
def home(): return "Welcome to BEE!"

@app.route('/about')
def about(): return "About BEE"
