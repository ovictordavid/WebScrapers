#LIBRARYS AND TOOLS

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import pandas as pd

#MAIN FUNCTION AND SUBFUNCTIONS
def get_opportunities_from_fiotec(url):
    # Version2.4 - 01.2023 - get local and data, one function structure, minor modifications
    # Oportunidades Fiotec 
    # Return dictionary containing opportunities from Fiotec which are open for candidate selection

    #SUB FUNCTIONS

    def show(data1, data2):  # Print opportunities and description

        opportunities = data1
        opport_dic_variables = data2
        num_opp = len(opportunities)

        if num_opp == 0:
            print("There are no opportunites open")
        else:
            print(f"Today we found {num_opp} opportunitie(s) and url(s): ")
            print()
            print("Here are the dic for each opportunitie")

            for k, v in opport_dic_variables.items():
                print('------------------------------------------------------------------------------------------------')
                print(k)
                print(v)

    def build_soup(url):  # build soup
        # requisition
        header = {'user-agent': 'Mozilla/105.0'}

        # get listview
        result = requests.get(url, header)
        soup_html = result.text
        soup_beaut = BeautifulSoup(soup_html, 'html.parser')

        return soup_beaut

    def scrapp_description(data_html):  # scrapper opportunities info

        # instantiate dicts
        result_dict = dict()
        dic_description = dict()

        # prerequisite
        institution = "Fiotec"
        institution_type = "FUN"  # Fundação
        scholarship_type = "Bolsa Fiotec"

        # get title
        title = data_html.find('h2', {'itemprop': 'name'}).text
        title = title.replace('\n', '').replace('\t', '')
        # print("title = " + title)

        # get scrapped from
        scrapped_from = ''

        # gets level from title and translate to our ID
        level = title.split()
        level_dict = {
            "Iniciação Científica": "IC",
            "Extensão": "EXT",
            "Técnico": "TEC",
            "Mestrado": "MASTER",
            "Doutorado": "PHD",
            "PD": "POSTDOC"
        }

        if level in level_dict.items():
            level = level_dict[level]
        else:
            level = "OTHER"

        # get main information opportunitie
        list_main = data_html.find('div', {'itemprop': 'articleBody'})

        # get description
        scrapp_description = list_main.find('p').text
        description = scrapp_description.replace('\xa0', ' ')

        # get date
        #registration_date
        registration_date = data_html.find_all('time', {'itemprop': 'datePublished'})
        registration_date = re.findall('[0-9][0-9][0-9][0-9][-][0-3][0-9][-][0-3][0-9]', str(registration_date))[0]
        Y,m,d = str(registration_date).split('-')
        registration_date = d+'/'+m+'/'+Y
        # registration_due_date - waiting for test
        registration_due_date = re.search(r".[0-9] de .* de [0-9][0-9][0-9][0-9]", description)[0]

        # list of paragr
        list_paragr = list_main.find_all('p')

        # interate every detailview
        for paragr in list_paragr[1:]:

            # get 'inclusão' title and info - info is not inside in a 'strong tag'
            if 'Inclusão' in paragr.text:
                k = paragr.find('strong').text
                v = paragr.text
                v = v.replace('Inclusão', '')

                dic_description[k] = v

            # get every title inside in a 'strong tag' and their description in next paragraph
            elif paragr.find('strong') != None:
                k = paragr
                v = k.find_next_sibling('p')

                if v.find('strong'):
                    v = k.find_next_sibling('ul')
                    v = v.text
                    v = v.replace('\n', '')

                else:
                    v = v.text
                    v = v.replace('\xa0', ' ')

                k = paragr.text
                dic_description[k] = v

            #get title and url for additional informations (PDF additional info)
            elif paragr == list_paragr[-1]:
                k = paragr.text
                k = k.replace('\xa0', '')
                v = paragr.find('a')
                v = v.get('href')
                v = 'https://www.fiotec.fiocruz.br/' + v
                dic_description[k] = v

        # get regime
        if "Regime jurídico" in dic_description:
            regime = dic_description['Regime jurídico']
        else:
            regime = "Not mentioned"

        # get scholarship
        if 'Bolsa' in regime:
            scholarship = 'Y'
            there_is_scholarship = True
        else:
            scholarship = 'N'
            there_is_scholarship = False

        # get n_jobs
        if 'Vagas' in dic_description:
            n_jobs = dic_description['Vagas']
        else:
            n_jobs = 'banco de currículos'

        # get study_field and prerequisite_course
        if "Formação necessária" in dic_description:
            study_field = re.search(r'área.* de .*.', dic_description["Formação necessária"])[0]
            prerequisite_course = dic_description["Formação necessária"]
            # print(study_field)
            # print(prerequisite_course)
        elif "Requisitos obrigatórios" in dic_description:
            prerequisite_course = dic_description["Requisitos obrigatórios"]
            # print(prerequisite_course)
            study_field = ''
        else:
            prerequisite_course = ''
            # print(prerequisite_course)
            study_field = ''
            # print('nada')

        # get prerequisite_other
        if "Requisitos obrigatórios" in dic_description:
            prerequisite_other = dic_description["Requisitos obrigatórios"]
        else:
            prerequisite_other = 'Not mentioned'

        # get required doc
        if "Inscrições" in dic_description:
            required_docs = dic_description['Inscrições']
        else:
            required_docs = 'Not mentioned'

        # get link
        if "Acesse mais informações sobre o processo seletivo." in dic_description:
            link = dic_description['Acesse mais informações sobre o processo seletivo.']
        else:
            link = "Not mentioned"

        #get city
        if "Local de atuação" in dic_description:
            city = dic_description["Local de atuação"]
        else:
            city = "Not mentioned"

        # zips into dict
        main_k = title
        result_dict['title'] = title
        result_dict['scrapped_from'] = scrapped_from
        result_dict['institution'] = institution
        result_dict['institution_type'] = institution_type
        result_dict['Level'] = level
        result_dict['description'] = description
        result_dict['regime'] = regime
        if there_is_scholarship: result_dict['scholarship'] = scholarship
        result_dict['n_jobs'] = n_jobs
        result_dict['study_field'] = study_field
        result_dict['prerequisite_course'] = prerequisite_course
        result_dict['prerequisite_other'] = prerequisite_other
        result_dict['required_docs'] = required_docs
        result_dict['required_docs'] = required_docs
        result_dict['link'] = link
        result_dict['city'] = city
        result_dict['registration_date'] = registration_date
        result_dict['registration_due_date'] = registration_due_date

        # print(result_dict)

        # possible fields
        # weekly_workhours - not mentioned in previous opportunities 01.2023
        # total_workhours - not mentioned in previous opportunities 01.2023
        # scholarship_value = '' - metioned in PDF
        #department = '' - specify in local variable

        return main_k, result_dict

    def build_opportunities_fiotec(dic_oportunities):  # build dic opportunities with description

        # print('test')
        dic_opport_descrip = dict()

        for v in dic_oportunities.values():
            soup = build_soup(v)
            k, v = scrapp_description(soup)
            dic_opport_descrip[k] = v

        # print(dic_opport_descrip)
        return dic_opport_descrip

    #MAIN FUNCTION
    # get listView - beaut soup fiotec open opportunities
    soup = build_soup(url)
    list_opportunities = soup.find_all('h2', {'itemprop':'name'})
    
    # get name opportunities and url description
    dic_opport = dict()
    
    for opportunities in list_opportunities:
        # get opportunities - acess <a> containing each detailView
        title = opportunities.find('a').text
        title = title.replace('\n\t\t\t\t\t\t','').replace('\t\t\t\t\t','')

        # get urls - acess <a> containing each detailView url, only href ones
        url = opportunities.find('a', {'itemprop':'url'}).get('href')

        # store the DetailView title opportunitie and Urls in a dic
        dic_opport[title] = 'https://www.fiotec.fiocruz.br'+url

    dic_opport_variables = build_opportunities_fiotec(dic_opport)
    show(dic_opport, dic_opport_variables)

    #for test
    #x = build_soup('https://www.fiotec.fiocruz.br/vagas-projetos/em-analise/8031-analista-de-sistemas-temporario')
    #scrapp_description(x)

#MAIN
get_opportunities_from_fiotec('https://www.fiotec.fiocruz.br/vagas-projetos/processo-de-selecao')