# Passerelle vers le demon Docker de l'arena.
#
# CTFd doit piloter le Docker de l'arena pour creer les instances par equipe.
# Le faire depuis le conteneur CTFd lui-meme ne marche pas : l'image CTFd n'a
# pas de client ssh, tourne en uid 1001, et son HOME n'est pas /root - la cle
# montee n'y serait donc ni lisible ni trouvee.
#
# Ce conteneur ouvre un tunnel ssh vers l'arena et republie le socket Docker
# distant en TCP sur le reseau interne du compose. CTFd s'y connecte avec
# DOCKER_HOST=tcp://dockerproxy:2375, sans avoir besoin de ssh.
#
# Le socket Docker distant n'est expose qu'en local (127.0.0.1:2381) ; seul
# broker.py (filtrant) ecoute sur 2375, attache QU'au reseau `internal` du
# compose (jamais `web`). Y acceder ne vaut plus root sur l'arena : le broker
# n'autorise que les operations de l'instancier et valide le corps de `create`.
FROM alpine:3.20

RUN apk add --no-cache openssh-client socat python3

COPY entrypoint.sh /entrypoint.sh
COPY broker.py /broker.py
RUN chmod +x /entrypoint.sh

EXPOSE 2375 7400
ENTRYPOINT ["/entrypoint.sh"]
