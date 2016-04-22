import tweepy
import datetime
import sys
import time
import json

#
# Verifica quais os limites ainda disponiveis para consumo da API do Twitter
#
def get_api_limits():

  print("Verificando limites da API...")

  # Pode ser que o programa ja se inicie com o limite de requisicoes estourado.
  rate_limit_available = False
  while not rate_limit_available:
    try:
      rate_limit = api.rate_limit_status()
      rate_limit_available = True
    except tweepy.error.RateLimitError as e:
      t = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M')
      print(t, "Limite para verificar os limites da API atingido. Vamos aguardar 60 seg...")
      sys.stdout.flush()
      time.sleep(60) 
    except tweepy.error.TweepError as e:
      t = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M')
      print(t, e," Vamos aguardar 60 seg...")
      sys.stdout.flush()
      time.sleep(60)

  user_timeline_remaining = int(rate_limit['resources']['statuses']['/statuses/user_timeline']['remaining'])
  rate_limit_remaining = int(rate_limit['resources']['application']['/application/rate_limit_status']['remaining'])

  print("Limit: "+str(rate_limit))
  print("user_timeline_remaining=",user_timeline_remaining)
  print("rate_limit_remaining=",rate_limit_remaining)

  return {'user_timeline_remaining': user_timeline_remaining,
          'rate_limit_remaining': rate_limit_remaining}


#
# Obtem uma pagina de tweets de um usuario especifico
#
def get_tweets(user, max_id):

  print("Recuperando 20 tweets de",user,"a partir do id",max_id,"...")

  limits = get_api_limits()

  # Vamos verificar dois limites: 
  #
  # . user_timeline_remaining     = requisicoes que ainda podem ser feitas
  #                                 para timeline de um usuario especifico
  # . rate_limit_status_remaining = requisicoes que ainda podem ser feitas 
  #                                 sobre qual o limite ainda disponivel 
  #                                 (sim, o twitter limite ate isso)
  #
  while(limits['user_timeline_remaining'] == 0 | limits['rate_limit_remaining'] == 0):
    print("Limite de acesso à API excedido. Vamos aguardar por 1 min...")
    sys.stdout.flush()
    time.sleep(60)    
    limits = get_api_limits()

  # Pode ser que aconteca de a chamada a seguir estourar
  # os limites de requisicoes da API, causando o erro:
  # tweepy.error.RateLimitError: [{'message': 'Rate limit exceeded', 'code': 88}]
  # Por isso fizemos o teste anterior, para que este erro nunca ocorra.

  try:
    timeline = api.user_timeline(user, max_id=max_id)
  except tweepy.error.TweepError as e:
    print("[ERRRO] Nao foi possivel recuperar tweets de",user,"com max_id=",max_id,"Erro:",e,"Vou ignorar e tocar adiante.")
    timeline = []

  return timeline


# Metodo que coleta todos os tweets da timeline
# de um usuario especifico.
def collect_user_timeline(user):

  print("Iniciando busca de tweets de", user)

  # Busca toda a timeline de um usuario especifico, 
  # conforme documentacao em:
  # http://tweepy.readthedocs.org/en/v3.5.0/api.html#API.user_timeline
  timeline = get_tweets(user,999999999999999999)

  # Vamos salvar os tweets de cada usuario em um arquivo diferente.
  tweets_file = open(user+"_tweets_"+agora+".txt", 'w')

  # Vamos contar a quantidade de tweets obtidos.
  i = 0

  # Imprime a quantidade de elementos obtidos.
  print(len(timeline),"tweets recuperados")

  # Enquanto houver elementos na timeline...
  while timeline:

    # A timeline eh composta por tweets.
    # O Twitter chama cada tweet de Status.
    # No tweepy, Status eh a classe (?!) definida em 
    # https://github.com/tweepy/tweepy/blob/master/tweepy/models.py#L73
    for status in timeline:

      i = i + 1

      # Na tela, imprime o resumo do tweet...
      print(user,i,status.id,status.created_at,status.text)
      # ... no arquivo, imprime o tweet (status) inteiro.
      #tweets_file.write(str(status._json)+"\n")
      tweets_file.write(json.dumps(status._json)+"\n")

      # Salva o ID do ultimo tweet coletado para ser usado 
      # na busca da proxima pagina de tweets.
      last_status_id = status.id

    # Busca a proxima pagina de tweets
    timeline = get_tweets(user,last_status_id-1)


  # Fecha o arquivo para que todas as informacoes enviadas
  # para ele sejam salvas com seguranca.
  tweets_file.close()

# Metodo principal do programa.
# Manda buscr os tweets de cada uma das contas de tweet 
# especificadas no array(?!) accounts.
def main():
  accounts = ['Cami_RojasV','Amarimatar','damian_ignacioB','ErvinCastillo',
              'DanielGedda','SebastianM_ra','jorgerauld','SaschaHannig',
              'gabriel_iturrac','CaroFigueroaCe','FEUAntofagasta','FeuachUACH',
              'FEUAI_stgo','FEUANDES','feubb','feuc','_FEUCEN','FEUDD_stgo',
              'Feuls','feusach','FEUSAM','feutfsm','feuv','la_fech','FECUdeC',
              'FEUFRO','FEDEPUDP','confech','creceruc','infestudiantes','Izquierda_Tuit',
              'izqautonoma','naupuc','jjcc_chile','UNE_CHILE','Rdemocratica',
              'camila_vallejo','GiorgioJackson','gabrielboric','Karolcariola',
              'EquipoJackson']
  for account in accounts:
    collect_user_timeline(account)

  print("Coleta finalizada das contas", accounts)


########################
#
# INICIO DO PROGRAMA
#
########################

# Recupera o instante atual na forma AnoMesDiaHoraMinuto
agora = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M')

# Registre sua aplicacao em https://apps.twitter.com
consumer_key="sua consumer_key"
consumer_secret="sua consumer_secret"
access_token="seu access_token"
access_token_secret="seu access_token_secret"



auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Verifica se eh para executar o metodo main()
if __name__ == "__main__": main()
