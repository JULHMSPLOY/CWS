@app.route('/choose_challenge', methods=['GET'])
def choose_challenge(self):
        challenges = {
            'Python': '/python',
            'MATLAB': '/matlab',
            'SQL': '/sql',
            'C': '/c'
        }