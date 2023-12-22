from mistery import *

class TriviaGame:

    def __init__(self, root, trivia=[]):
        self.root = root
        self.question_number = 0
        self.score = 0


        # Creazione di righe e colonne "fittizie" per centrare la label e uniformare i bottoni
        for i in range(4):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1, uniform='equal')
         
 
        self.questions = []
        if len(trivia)==0:
            self.questions = [
                {
                    "question": "Quale è il più lungo fiume del mondo?",
                    "options": ["Nilo", "Amazonas", "Mississippi", "Gange"],
                    "correct_answers": ["Nilo"]
                }
            ]
        else:
            self.todays_numbers = get_sequenza_numeri(len(trivia))
            print(self.todays_numbers)
            #prende le domande univoche per questo giorno
            for i in self.todays_numbers:
                self.questions.append(trivia[i-1])
        
        self.question_label = tk.Label(root, text="", font=("Arial", 16))
        self.question_label.grid(row=0, column=1, columnspan=2, sticky="n")
        
        self.pt_label = tk.Label(root, text="Punti conoscenza ottenuti: 0", font=("Arial", 7))
        self.pt_label.grid(row=0, column=3, columnspan=1, sticky="n")
        
        self.option_buttons = []
        
        
        intro_message = '''Benvenuto nel mondo di "MindQuest: Il Viaggio dell'Essere".
        
        
In MindQuest, ti invitiamo a un'avventura unica e strana, un viaggio attraverso le profondità della conoscenza. 

Questo non è solo un gioco, ma un'esplorazione interiore progettata per connetterti con te stesso, valutare la tua prontezza mentale e guidarti verso una consapevolezza maggiore della tua esistenza.

Il tuo viaggio inizia con un test, un insieme di domande attentamente selezionate per sondare il tuo pensiero, le tue emozioni e le tue percezioni. Avrai a disposizione 12 risposte per ciascuna domanda, dove potrebbero esserci più risposte valide.
È un'opportunità per riflettere, esplorare e capire te stesso più a fondo.

Tuttavia, c'è un limite: per preservare l'esperienza e garantire un'assimilazione graduale delle scoperte, il gioco ti offrirà un massimo di 5 domande al giorno. 
Ogni giorno, ti verranno presentati contenuti diversi, nuove sfide e nuove possibilità di esplorazione.

MindQuest è progettato per essere un viaggio ponderato, dove ogni passo conta e ogni risposta porta a nuove scoperte. È un invito a imparare, crescere e scoprire chi sei veramente.

Sii pronto a metterti in gioco, a esplorare i confini della tua mente e a lasciarti guidare in un viaggio unico, verso la comprensione di te stesso e del mondo che ti circonda.

Buon viaggio, esploratore della mente.
        '''
        
        risposta = messagebox.askokcancel("MindQuest: Il Viaggio dell'Essere", intro_message)
        if not risposta:
            messagebox.showinfo("AS YOU DESIRE!", "Va bene, ciao")
            sys.exit()
        
        self.update_question()

    def update_question(self):
        if self.question_number < len(self.questions):
            question_data = self.questions[self.question_number]
            self.question_label.config(text=question_data["question"])
            
            for i, option in enumerate(question_data["options"]):
                button = tk.Button(self.root, text="", font=("Arial", 12), command=lambda idx=i: self.check_answer(idx), wraplength=120)
                row = (i // 4) + 1
                col = i % 4
                button.grid(row=row, column=col, columnspan=1, padx=5, pady=5, sticky="nsew")  
                self.option_buttons.append(button)
                self.option_buttons[i].config(text=option)

            self.question_number += 1
        else:
            self.show_result()

    def check_answer(self, idx):
        selected_option = self.option_buttons[idx].cget("text")
        correct_answers = self.questions[self.question_number - 1]["correct_answers"]

        if selected_option in correct_answers:
            self.score += 1
        else:
            messagebox.showinfo("Nope", f"Era un altra..")
            
        self.pt_label.config(text=f"Punti conoscenza ottenuti: {self.score}")
        
        #reset dei bottoni
        for button in self.option_buttons:
            button.destroy()
        del self.option_buttons[:]  # Elimina anche i riferimenti nell'array
        self.option_buttons = []
        
        self.update_question()

    def show_result(self):
        self.question_label.config(text=f"Hai risposto correttamente a {self.score} domande su {len(self.questions)}!")
        self.pt_label.destroy()
        
        
        self.result_label= tk.Label(self.root, text="", font=("Arial", 14))
        self.result_label.grid(row=2, column=1, columnspan=2, sticky="n")
        
        
        while self.score>0:
            self.result_label.config(text=f"Ti verranno mostrati {self.score} video clip")
    
            chosen_file = self.todays_numbers[self.score]
            self.score = self.score -1
            play_decrypted_video_from_zip(chosen_file)
        if os.path.isfile('./ffplay.exe'):   
            os.remove('./ffplay.exe')
            
        self.result_label.config(text=f"Hai visto tutte le clip :)")
            




def main():

    # Esegui il download dei trivia e dei video, se necessario
    trivia = check_trivia_online()
    print(trivia)
    root = tk.Tk()
    root.title("MindQuest: Il Viaggio dell'Essere")
    root.geometry("800x600")
    root.resizable(False, False)  # (larghezza, altezza)
    game = TriviaGame(root, trivia)

    root.mainloop()

if __name__ == "__main__":
    main()
    

