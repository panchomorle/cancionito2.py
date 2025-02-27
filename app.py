from flask import Flask, request
import sett
import services

app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    imagen = "<img src='https://roico.com/wp-content/uploads/2016/05/ROI_Headshot_John-Pollack.jpg'>"
    return imagen

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto',403
    except Exception as e:
        return e,403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        ## text = messages['text']['body']
        #Lo extraigo a una funcion en services para manejar el type
        text = services.obtener_mensaje_whatsapp(message)
        number = services.filtrar_number(number) #El number viene cambiado (+549), manejo para eliminar el 9 extra
        
        ##Este proceso está demorando más de 30s
        services.administrar_chatbot(text, number, messageId, name)

        return 'enviado'
    except Exception as e:
        print("hubo un error al recibir el mensaje")
        print("Excepción: "+str(e))
        return 'no enviado'+str(e)

if __name__ == '__main__':
    app.run()