 # import libraries ->
import mysql.connector
import typer
from rich import print


 # main function ->
def __main():
  print('[bold blue]⁕ function loading...[/bold blue]')

  config = {
    'user': 'root',          # changes this values
    'password': 'password',  # changes this values
    'host': '127.0.0.1',     # changes this values
    'database': 'testdb'
  }

  conn = None
  cursor = None

  try:
     # database => conection
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

     # database => table creation
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS users (
          id INT AUTO_INCREMENT PRIMARY KEY,
          username VARCHAR(50),
          password VARCHAR(50),
          role VARCHAR(20)
      )
    ''')

     # data => example inserts (avoid duplicates)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
      cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin_pass', 'admin')")
      cursor.execute("INSERT INTO users (username, password, role) VALUES ('user', 'user_pass', 'user')")
      conn.commit()

     # funciton => vulnerable sql injection
    def __loginVulnerable(username, password):
       # build this around the input -> vulnerable
      query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
      print("Ejecutando consulta vulnerable:", query)
      cursor.execute(query)
      return cursor.fetchone()

     # function => secure login with prepared statement
    def __loginSecure(username, password):
      query = "SELECT * FROM users WHERE username = %s AND password = %s"
      print("Ejecutando consulta segura:", query)
      cursor.execute(query, (username, password))
      return cursor.fetchone()

     # data input => malware simulation
    user_input_username = input("Introduce el nombre de usuario: ")  # Ejemplo: admin
    user_input_password = input("Introduce la contraseña: ")         # Ejemplo: ' OR '1'='1

    if not user_input_username or not user_input_password:
      print('[bold yellow] > inputs cannot be empty.[/bold yellow]')
      return

     # try login => vulnerable function
    print("\n[bold yellow]--- login vulnerable ---[/bold yellow]")
    user = __loginVulnerable(user_input_username, user_input_password)

    if user:
      print(f"[bold green] > greateful login! user: {user[1]}, rol: {user[3]}[/bold green]")
    else:
      print('[bold red] > failed login.[/bold red]')

     # try login => secure function
    print("\n[bold yellow]--- login seguro (prepared statement) ---[/bold yellow]")
    user_secure = __loginSecure(user_input_username, user_input_password)

    if user_secure:
      print(f"[bold green] > greateful login! user: {user_secure[1]}, rol: {user_secure[3]}[/bold green]")
    else:
      print('[bold red] > failed login.[/bold red]')

  except mysql.connector.Error as err:
    print(f'[bold red] > database error: {err}[/bold red]')
  finally:
     # sesion => close
    if cursor:
      cursor.close()
    if conn:
      conn.close()


 # secure function boot ->
if __name__ == "__main__":
  typer.run(__main)
