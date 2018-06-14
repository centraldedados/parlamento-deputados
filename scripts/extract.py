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
import roman

data_dir = "../../parlamento/"

biolist = []   # Bios
infolist = []  # Info sobre atividade

CURRENT_LEG = 13

SHORTNAME_REPLACES = {
    'Alberto Araujo': 'Alberto Araújo',
    'Alberto Oliveira e Silva': 'Oliveira e Silva',
    'António de Almeida Santos': 'Almeida Santos',
    'António Sousa Lara': 'Sousa Lara',
    'Carlos Costa': 'Carlos da Costa',
    'Guilherme de Oliveira Martins': 'Guilherme d\'Oliveira Martins',
    'José Judas': 'José Luís Judas',
    'Luís Kalidas Barreto': 'Luís Kalidás Barreto',
    'Mário Montalvão Machado': 'Montalvão Machado',
    'Mata Cáceres': 'Mata de Cáceres',
    'Raul Castro': 'Raúl Castro',
    'Raúl Rêgo': 'Raul Rêgo',
    'Raul Rego': 'Raul Rêgo',
    'Rosa Maria Bastos Albernaz': 'Rosa Maria Albernaz',
    'Vitor Crespo': 'Vítor Crespo',
}

# Deputados duplicados, lista para unificar com um único ID
ID_REPLACES = {
    4736: 3457,  # Artur Beleza de Oliveira
    3346: 4742,  # Beatriz Cal Brandão
    4788: 3036,  # Magalhães Mota
    3347: 4821,  # Vilhena de Carvalho
    3304: 1460,  # António Dias da Costa
    4727: 3447,  # António Fontes
    3345: 4781,  # João Nascimento Guerra
    3073: 316,   # Rui Almeida Mendes
    4850: 125,   # Nuno Delerue
}

ID_SHORTNAMES = {
    2965: "Cristóvão Guerreiro Norte",
    1695: "Manuel Ferreira Martins",
    2170: "Manuel da Conceição Pereira",
    3403: "Domingos da Silva Pereira",
    856: "João Almeida Alves",
    3418: "João Gonçalves Marques",
    3451: "João Oliveira Marques",
    3389: "João Ribeiro Rodrigues",
    3251: "Carlos Rodrigues Matias",
    29: "Carlos Lopes Pereira",
    1132: "António Costa Rodrigues",
    1548: "Dinis Prata Costa",
    1360: "Paulo Santos Neves",
    1634: "Carla Tavares Gaspar",
    2064: "Jorge Magalhães da Costa",
}

legs = range(2, CURRENT_LEG + 1)

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

mps = {}
for bio in biolist:
    mp = OrderedDict()
    mandate = bio['cadDeputadoLegis']['pt_ar_wsgode_objectos_DadosDeputadoLegis']
    if isinstance(mandate, list):
        mandate = mandate[0]

    mp['id'] = int(bio['cadId'])
    shortname = utils.lower_given_name(mandate['depNomeParlamentar']).replace("  ", " ").replace(' De ', ' de ').replace(' E ', ' e ')
    if shortname in SHORTNAME_REPLACES:
        mp['shortname'] = SHORTNAME_REPLACES[shortname]
    elif mp['id'] in ID_SHORTNAMES:
        mp['shortname'] = ID_SHORTNAMES[mp['id']]
    else:
        mp['shortname'] = shortname
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

    if bio.get('cadHabilitacoes'):
        mp['education'] = []
        node = bio['cadHabilitacoes']['pt_ar_wsgode_objectos_DadosHabilitacoes']
        if isinstance(node, list):
            for item in node:
                if 'habDes' in item:
                    mp['education'].append(item['habDes'].strip('.'))
        else:
            if 'habDes' in item:
                mp['education'].append(node['habDes'].strip('.'))
    if 'education' in mp and not mp.get('education'):
        del mp['education']

    if bio.get('cadCargosFuncoes'):
        mp['jobs'] = []
        node = bio['cadCargosFuncoes']['pt_ar_wsgode_objectos_DadosCargosFuncoes']
        if isinstance(node, list):
            for item in node:
                if item['funAntiga'] == 'S':
                    mp['jobs'].append(item['funDes'].strip(';'))
                else:
                    if not mp.get('current_jobs'):
                        mp['current_jobs'] = []
                    mp['current_jobs'].append(item['funDes'].strip(';'))
        else:
            if node['funAntiga'] == 'S':
                mp['jobs'].append(node['funDes'].strip(';'))
            else:
                if not mp.get('current_jobs'):
                    mp['current_jobs'] = []
                mp['current_jobs'].append(node['funDes'].strip(';'))
    # mp['commissions']

    if bio.get('cadCondecoracoes'):
        mp['awards'] = []
        node = bio['cadCondecoracoes']['pt_ar_wsgode_objectos_DadosCondecoracoes']
        if isinstance(node, list):
            for item in node:
                mp['awards'].append(item['codDes'])
        else:
            mp['awards'].append(node['codDes'])

    mp['url_parlamento'] = 'http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID={}'.format(mp['id'])
    mp['url_democratica'] = 'http://demo.cratica.org/deputados/{}/'.format(mp['slug'])
    mp['url_hemiciclo'] = 'http://hemiciclo.pt/{}/{}'.format(mp['party'].lower().replace('-pp', ''), mp['id'])
    mp['image_url'] = 'http://app.parlamento.pt/webutils/getimage.aspx?id={}&type=deputado'.format(mp['id'])
    mp['mandates'] = []

    '''
    # já está gravado?
    results = list(filter(lambda other_mp: other_mp['id'] == mp['id'], [mps[key] for key in mps]))
    if bool(results):
        # remover o resultado anterior e substituir pelo mais recente
        other_mp = results[0]
        mps.pop(mp['shortname'])
    '''
    if mp['id'] in ID_REPLACES:
        # casos especiais de um deputado que está duplicado na DB do Parlamento
        continue
    mps[mp['shortname']] = mp

for info in infolist:
    # encontrar o deputado correspondente a esta entrada
    id = int(info['depCadId'])
    if id in ID_REPLACES:
        id = ID_REPLACES[id]
    '''
    mp = list(filter(lambda mp: mp['shortname'].upper == info['depNomeParlamentar'], [mps[key] for key in mps]))
    '''
    mp = [mps[key] for key in mps if mps[key]['id'] == id]
    if len(mp) != 1:
        print("há problema no filtro")
        print(id)
        print(info)
        print(len(mp))
    mp = mp[0]

    # acrescentar mandato
    mandate = OrderedDict()
    mandate["legislature"] = roman.fromRoman(info["legDes"])
    partyinfo = info["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]
    if isinstance(partyinfo, list):
        # mais do que um partido durante uma legislatura
        # FIXME: para já só gravamos o último, devíamos conseguir registar isto
        mandate["party"] = partyinfo[-1]["gpSigla"]
    else:
        mandate["party"] = partyinfo["gpSigla"]
    mandate["constituency"] = utils.lower_given_name(info["depCPDes"])

    # situação
    sit = info['depSituacao']['pt_ar_wsgode_objectos_DadosSituacaoDeputado']
    if not isinstance(sit, list):
        # print(sit)
        if not sit.get("sioDtFim") and mandate["legislature"] == CURRENT_LEG:
            mp['active'] = True
            # mandate['end_date'] = ""
        mandate['start_date'] = sit["sioDtInicio"]
        mandate['end_date'] = sit.get("sioDtFim")
    else:
        for item in sit:
            if item['sioDes'].startswith("Efetiv"):
                if not item.get("sioDtFim") and mandate["legislature"] == CURRENT_LEG:
                    mp['active'] = True
                mandate['start_date'] = item["sioDtInicio"]
                mandate['end_date'] = item.get("sioDtFim")
            else:
                print(item['sioDes'])
    mandate["activity_url"] = "http://www.parlamento.pt/DeputadoGP/Paginas/ActividadeDeputado.aspx?BID={}&lg={}".format(mp['id'], info["legDes"])
    mp["mandates"].append(mandate)

# inverter as listas dos mandatos
for key in mps:
    mps[key]['mandates'].reverse()

# ordenar por ordem alfabética
mps = OrderedDict(sorted(mps.items(), key=lambda k: k[1]['slug']))

# test suite da treta
active_mps = [mps[key] for key in mps if mps[key].get("active")]
print(len(active_mps))
# assert len(active_mps) == 230

with open('deputados.json', 'w') as f:
    f.write(json.dumps(mps, indent=2, ensure_ascii=False))

fields_to_remove = ['mandates', 'awards', 'jobs', 'current_jobs', 'education']
with open('deputados.csv', 'w') as f:
    keys = list(mps["Abílio Curto"].keys())
    for field in fields_to_remove:
        if field in keys:
            keys.remove(field)
    writer = csv.DictWriter(f, keys)
    writer.writeheader()
    for row in mps:
        for field in fields_to_remove:
            if field in mps[row]:
                del mps[row][field]
        writer.writerow(mps[row])
