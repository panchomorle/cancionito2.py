import requests # type: ignore
import sett
import json
import regex #para eliminar caracteres no alfanuméricos
import random as r

def obtener_mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']

    return text

def filtrar_number(number):
    if number[0:3] == "549": 
        car = "54"
        num = number[3:]
        number = (car+num)
    return number

def enviar_mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Access-Control-Allow-Origin': '*',
                   'Authorization': 'Bearer '+whatsapp_token}
        
        response = requests.post(url=whatsapp_url, headers=headers, data=data)
        if response.status_code == 200:
            #print("se envió"+str(data))
            return 'mensaje enviado'
        else:
            print("El status code es: "+str(response.status_code))
            print("El mensaje era: "+str(data))
            return 'mensaje no enviado', response.status_code
    except Exception as e:
        return e,403
    

def text_message(number, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def image_message(number, url):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "image",
            "image": {
                "link": url
            }
        }
    )
    return data

#--------funcion que permite enviar canción entera si tiene más de 1 pág-----------
def enviar_cancion(number, id):
    #traigo el json de las canciones de esa imagen y parseo a dict
    res = requests.get(sett.api_cancionito+"songs/"+str(id)+"/images")
    if res.status_code == 200:
        images = res.json()  # Obtiene la respuesta como JSON
    else:
        images = [] 
    for obj in images:
        data = image_message(number, obj["url"])
        enviar_mensaje_whatsapp(data)

def normalizar_string(text: str):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    texto_lower = text.lower() #convierto todo a minusculas
    for a, b in replacements: #reemplazo los 'a' de la tupla por los 'b' de la tupla
        texto_lower = texto_lower.replace(a, b)
    texto_limpio = regex.sub(r'[^\w\s\n]', '', texto_lower) #quito los no alfanuméricos con regex
    texto_normalizado = texto_limpio.strip() #acá le quito los espacios de atrás y adelante
    return texto_normalizado

def normalizar_array(array: list):
    array_normalizado = []
    for text in array:
        array_normalizado.append(normalizar_string(text))
    return array_normalizado

def elegir_random(posibles_canciones: dict):
    indice = r.randint(0, len(posibles_canciones)-1)
    return posibles_canciones[indice]

def administrar_chatbot(text, number, messageId, name):
    texto = normalizar_string(text) ##sin Special Characters y en lower
    #lista_songs = json.loads(requests.get(sett.api_cancionito+"songs")) #get all canciones
    res = requests.get(sett.api_cancionito + "songs")
    if res.status_code == 200:
        lista_songs = res.json()  # Obtiene la respuesta como JSON
    else:
        lista_songs = []  # Manejar error, lista vacía o alguna otra acción

    posibles_saludos=['hola', 'alo', 'hi', 'hello', 'ola', 'buenas', 'buen dia', 'buenos dias', 'good morning', 'how are you', 'como estas', 'que tal']
    if any(saludo == texto for saludo in posibles_saludos):
        data = text_message(number, f"¡Hola! Mi nombre es CancioNito🎵. Podes pedirme:\n- Una canción por título\n- Una lista de canciones separadas por enter\n- Sugerencias escribiendo 'sugerencias'\n- Una canción aleatoria escribiendo 'random'\nDios te bendiga!💫")
        enviar_mensaje_whatsapp(data)
    elif "random" == texto or "ramdom" == texto:
        id_song = elegir_random(lista_songs)["id"]
        enviar_cancion(number, id_song) #envio la imagen random
    elif "sugerencias" == texto:
        sugerencias = '\n'.join(elegir_random(lista_songs)["title"] for _ in range(3)) if True else ''
        data = text_message(number, sugerencias)
    else: #---------------------------MOTOR PRINCIPAL: CHECKEO DE CANCIONES-----------------------
        #SEPARO EL TEXTO DEL USUARIO POR SALTOS DE LINEA PARA VER SI SON CANCIONES
        texto_separado = texto.split("\n") #array de canciones pedidas por el usuario
            #COMPRUEBO QUE CADA LINEA SEA UNA CANCION VÁLIDA:
        for txt in texto_separado:  # Itero sobre las canciones del usuario
            match_found = False  # Variable para indicar si se encontró una coincidencia
            for song in lista_songs:  # Itero sobre las canciones de la BDD
                if song["title"] == txt:  # Ignorar mayúsculas/minúsculas si es necesario
                    enviar_cancion(number, song["id"])
                    match_found = True  # Se encontró una coincidencia
                    break  # Rompo el ciclo interno ya que ya se encontró la canción
            
            # Si no se encontró ninguna coincidencia, enviar el mensaje de error
            if not match_found:
                enviar_mensaje_whatsapp(text_message(number, f'No se encontraron coincidencias para "{txt}", prueba escribirla de otra forma!'))