======
CyfLib
======

Cyfnet Python Library (CyfLib) es una librería de código abierto para python. Lo que se pretende con esta librería es facilitar la escritura del código en Python.

Clases
======

CyfLib incluye varias clases, para organizar mejor el código. Se pueden importar todas o solo una especifica.
Hay las siguientes clases:

* ProgressBar. Clase para construir facilmente barras de progreso y evitar largas líneas de código. Es fácil de
  manejar y es bastante personalizable.

* BitCoin. Lista de funciones relacionadas con BitCoin fuera de línea.

* ConfigManager. Un gestor de configuración para facilitar la escritura de código, fácil de utilizar.

CyfLib se puede importar usando:

import CyfLib 

No hace falta from, ya que CyfLib se encarga de asignar automaticamente los archivos a las funciones y clases.

ProgressBar
------------

La clase ProgressBar() de CyfLib permite crear barras de progreso fácilmente. Estas barras son altamente personalizables (vía **kwargs o modificando el código).
Para crear una barra es muy fácil. Obviamente CyfLib debe estar importado anteriormente.

1. Se personaliza la barra con **kwargs. Se crea un diccionario que puede contener los siguientes valores:

* str "char_full" Indica el carácter cuando la barra está llena

* str "char_empty" Indica el carácter cuando la barra está vacía

* int "width" Indica la anchura de la barra (por defecto: 20)

* bool "percentage" Usa los valores True/False para indicar si se muestra el porcentaje al lado de la barra

args = {"char_full":"/", "char_empty":" ", "width":30, "percentage":True}

2. Se crea la barra configurada. El valor args es opcional (se requieren ** para especificar que se trata de kwargs)

p = cyflib.ProgressBar(**args)

3. La barra ya está creada (aunque no se muestra nada en pantalla). Se pueden usar diferentes comandos.

* p.Update() Muestra la barra de progreso. Si no se imprime nada en pantalla entre dos p.Update(), la barra se conservará en la misma línea, ya que usa la funcion stdout() del paquete sys.

* p.Update(msg) Muestra la barra de progreso, junto a un mensaje (msg)

* p.Increment(int) Se incremente el porcentaje int. El valor se incrementa, es decir que si usamos dos veces seguidas p.Increment(25), el valor será 50, no 25.

* p.Reset() Resetea el porcentaje a 0.

* p.Percentage() Devuelve el porcentaje de la barra.

* p.PrintBar() Imprime la barra en pantala sin usar sys.stdout(), eso significa que si se llama más de una vez, imprimira la barra en más de una línea. No se recomienda usar está función.

Puedes encontrar más tutoriales en http://cyfnet.com/cyflib

BitCoin
---------

La clase BitCoin() de CyfLib pretende facilitar líneas de código relacionadas con el sistema BitCoin. No se conecta a los servidores de BitCoin, por lo tanto es offline. Hay algunas funciones interesantes en esta librería, pero antes debemos crear la función con:

btc = cyflib.BitCoin()

Luego de esto se puede usar con btc.funcion()

Funciones de BitCoin():

* GetAddress(semilla) Crea una dirección de monedero BitCoin a partir de una semilla.

* GetPrivateKey(semilla) Crea una clave privada de BitCoin a partir de una semilla.

* CheckBalance(direccion) Comprueba el saldo de una dirección BitCoin usando la API de BlockChain. Se requiere internet.

* ConvertAmount(cantidad) Transforma la cantidad devuelta por CheckBalance() a BTC.

* AddressByPrivateKey(clave_privada) Genera una dirección de monedero BitCoin a partir de una clave privada. Si es la misma clave privada, la dirección siempre será la misma.

* RandomSeed() Genera una semilla aleatoria segura para usarla para crear claves privadas, usando: key = btc.GetPrivateKey(btc.RandomSeed()), así la semilla nunca se sabrá y la clave privada será más segura.

Atención: no recomendamos usar BitCoin() para usuarios inexpertos que no entiendan como funciona el sistema BitCoin. CyfNet no se responsabiliza de nada usando esta clase.

ConfigManager
-------------

La clase ConfigManager() es un fácil gestor de archivos de configuración para Python. Permite la escritura de variables en archivos y su modificación, encriptando el archivo. CyfLib se encarga de todo el código, tu solo debes utilizar las siguientes funciones, pero antes debes llamar al archivo con:

a = cyflib.ConfigManager(archivo, encriptacion)
#archivo = el archivo de configuracion
#encriptacion = por defecto True, encripta el archivo con una contraseña constante.

Funciones de ConfigManager:

* a.Create() Crea el archivo de configuración (si se vuelve a usar se reiniciará el archivo)

* a.Load() Carga el archivo. Solo se debe usar al principio del programa

* a.SetValue(variable, valor) Establece una variable con un valor

* a.GetValue(variable) Devuelve el valor de variable

* a.Save() Guarda de nuevo el archivo, es recomendable hacerlo al final del programa, cuando se guarde y se quiera volver a utilizar se deberá usar a.Load() o a.Reload() para recargar el archivo

Fin de las funciones de CyfLib, puedes visitar http://cyfnet.tk/cyflib para informarte más de CyfLib.
