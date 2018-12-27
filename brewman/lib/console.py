
def confirm(msg):
    while True:        
        confirm=input(msg).upper()
        if confirm == 'N' or confirm == 'NO':            
            # change this to raise a error. catch him and stop all threads
            raise(KeyboardInterrupt)
        elif confirm == 'Y' or confirm == 'Yes' or confirm == '':
            break
        else:
            print("Unkown Input. Use Y or N")
