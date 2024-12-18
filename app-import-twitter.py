import tweepy
import time

# Insira suas credenciais da API
API_KEY = '7svcEUDWJ2ytGukVx55GCRix7'
API_SECRET_KEY = 'AcpFF9ryJQZIspD767f4gaj05jXEoyafgOlhL0rD7fhf8GnDUk'
ACCESS_TOKEN = '1864836180266881025-N2KlRbM573Rac6hRfMnJFaoIr6rNxd'
ACCESS_TOKEN_SECRET = 'Zq7kamMUeifWGSyis6xghrVSU5RbPpDPgfpmu4pAs7MPe'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAACaJxQEAAAAAFBCOZQwPG%2F7LFKUiYeKBXOZDH%2Bk%3DDB68nefIyo5oKFGYehuhk9V3jsI8CZgH7wz8qwXl1ubRXQh7p0'

# Autenticação com a API v2 (Bearer Token)
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Usuário para o qual queremos buscar tweets
username = 'Mecuido_'

try:
    # Obter o ID do usuário
    user = client.get_user(username=username)
    user_id = user.data.id

    while True:
        try:
            # Buscar os tweets do usuário
            tweets = client.get_users_tweets(id=user_id, max_results=10)
            
            # Exibir os tweets
            if tweets.data:
                for tweet in tweets.data:
                    print(f'{tweet.id}: {tweet.text}')
            else:
                print("Nenhum tweet encontrado.")
            break  # Saia do loop se a requisição for bem-sucedida
        except tweepy.errors.TooManyRequests:
            print("Limite de requisições atingido. Aguardando 15 minutos...")
            time.sleep(900)  # Aguarde 15 minutos antes de tentar novamente
        except tweepy.errors.TweepyException as e:
            print(f"Erro ao buscar tweets: {e}")
            break

except tweepy.errors.TweepyException as e:
    print(f"Erro ao obter o usuário: {e}")
