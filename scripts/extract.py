#!/usr/bin/env python3
'''
Extrai a info dos deputados dos JSON vindos do site do Parlamento.
Recorre aos datasets Registo Biográfico e Info Base
'''
import os
import json
import csv
from collections import OrderedDict
import utils

data_dir = "../../parlamento/"

# Bios
biolist = []
# Info sobre atividade
infolist = []
# Registos de interesses
rgilist = []

legs = range(2, 14)

for leg in legs:
    # legislaturas 2 a 13
    if not str(leg).startswith("1"):
        leg = "0" + str(leg)

    biofile = os.path.join(data_dir, "data/registo-biografico-{}.json".format(leg))
    biodata = json.load(open(biofile, 'r'))
    biolist.extend(biodata["RegistoBiografico"]["RegistoBiograficoList"]["pt_ar_wsgode_objectos_DadosRegistoBiograficoWeb"])

    infofile = os.path.join(data_dir, "data/info-base-{}.json".format(leg))
    infodata = json.load(open(infofile, 'r'))
    infolist.extend(infodata["Legislatura"]["Deputados"]["pt_ar_wsgode_objectos_DadosDeputadoSearch"])
    # rgilist.extend(biodata["RegistoBiografico"]["RegistoInteressesV2List"])

mps = []
for bio in biolist:
    mp = OrderedDict()
    mandate = bio['cadDeputadoLegis']['pt_ar_wsgode_objectos_DadosDeputadoLegis']
    if isinstance(mandate, list):
        mandate = mandate[0]

    mp['id'] = int(bio['cadId'])
    mp['shortname'] = mandate['depNomeParlamentar']
    mp['slug'] = utils.slugify(mp['shortname'])
    mp['name'] = utils.lower_given_name(bio['cadNomeCompleto'])
    mp['gender'] = bio['cadSexo']
    mp['party'] = mandate['gpSigla']
    mp['active'] = False
    # mp['education']
    mp['birthdate'] = bio.get('cadDtNascimento')  # pode não existir
    prof = bio.get('cadProfissao', '').strip()  # pode não existir
    # determinar se há 2 profissões
    if not prof.startswith('Jurista (advogado c'):  # caso especial
        if '/' in prof:
            mp['occupation'] = prof.split('/')[0].strip()
            mp['occupation2'] = prof.split('/')[1].strip()
        elif ',' in prof:
            mp['occupation'] = prof.split(',')[0].strip()
            mp['occupation2'] = prof.split(',')[1].strip()
        else:
            mp['occupation'] = prof
            mp['occupation2'] = ''
    else:
        mp['occupation'] = prof
        mp['occupation2'] = ''
    # mp['current_jobs']
    # mp['jobs']
    # mp['commissions']
    # mp['mandates']
    # mp['awards']
    mp['url_parlamento'] = 'http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID={}'.format(mp['id'])
    mp['url_democratica'] = 'http://demo.cratica.org/deputados/{}/'.format(mp['slug'])
    mp['url_hemiciclo'] = 'http://hemiciclo.pt/{}/{}'.format(mp['party'].lower().replace('-pp', ''), mp['id'])
    mp['image_url'] = 'http://app.parlamento.pt/webutils/getimage.aspx?id={}&type=deputado'.format(mp['id'])

    # já está gravado?
    results = list(filter(lambda other_mp: other_mp['id'] == mp['id'], mps))
    if bool(results):
        # remover o resultado anterior e substituir pelo mais recente
        other_mp = results[0]
        mps.remove(other_mp)
    mps.append(mp)

for info in infolist:
    id = int(info['depCadId'])
    # encontrar o deputado correspondente a esta entrada
    mp = list(filter(lambda mp: mp['id'] == id, mps))
    if len(mp) != 1:
        print("há problema no filtro")
        print(mp)
        print(len(mp))
    mp = mp[0]
    # situação
    sit = info['depSituacao']['pt_ar_wsgode_objectos_DadosSituacaoDeputado']
    if not isinstance(sit, list):
        # print(sit)
        if not sit.get("sioDtFim"):
            mp['active'] = True
    else:
        for item in sit:
            if item['sioDes'].startswith("Efetiv") and not item.get("sioDtFim"):
                mp['active'] = True
                break

# ordenar por ordem alfabética
mps = sorted(mps, key=lambda k: k['slug'])

# test suite da treta
active_mps = [mp for mp in mps if mp.get("active")]
assert len(active_mps) == 230


with open('deputados.csv', 'w') as f:
    writer = csv.DictWriter(f, mps[0].keys())
    writer.writeheader()
    writer.writerows(mps)
