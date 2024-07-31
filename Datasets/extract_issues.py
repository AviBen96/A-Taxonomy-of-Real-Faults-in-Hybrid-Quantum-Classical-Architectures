##Created by Avner Bensoussan
## Copyright 20/01/2024
import time
from datetime import date
import requests
import xlsxwriter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

QUERIES = ['VQE', 'VQA','Variational Quantum eigensolvers', 'Variational Quantum algorithm', 'Quantum Annealing', 'Gaussian boson sampling',
'Analog quantum simulation', 'Digital-analog quantum simulation and computation','Iterative quantum assisted eigensolver',
'Quantum Approximative Optimisation Algorithms', 'QAOA', 'Quantum Machine Learning', 'tfq', 'tensorflow quantum']

def scrap(query):
    scrap.nbr_results = 0
    scrap.row = 1
    scrap.page = 1
    scrap.is_results = True
    worksheet = workbook.add_worksheet(query[:30])
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 20)

    worksheet.write('A1', 'Issue Title', bold)
    worksheet.write('B1', 'Link', bold)
            
    def search(ranges = None):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        
        while scrap.is_results:
            if scrap.page % 9 == 0:
                # Avoid Github query limitation
                driver.close()
                driver = webdriver.Chrome(ChromeDriverManager().install())
            
            if ranges is None:
                search = 'https://github.com/search?q=' + query + '+++label%3Abug&type=issues&state=closed&p=' + str(scrap.page)
            
            else:
                search = 'https://github.com/search?q=' + query + '+++label%3Abug++++comments%3A'+ str(ranges[0]) + '..' + str(ranges[1]) + '&type=issues&state=closed&p=' + str(scrap.page)
                
            driver.get(search)
            delay = 3 
            
            try:
                # Wait for the search results to appear
                WebDriverWait(driver, delay).until(
                        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, f"[data-testid='results-list']"))
                    )
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                nb_results = soup.find('div', class_='Box-sc-g0xbh4-0 cgQapc').text
                            
                if 'k' in nb_results:
                    print(nb_results)
                    print('Dividing into sub-searches')
                    driver.close()
                    sub_search()
                    break
                
                else:
                    results_list = soup.find('div', attrs={'data-testid': 'results-list'}).find_all('div', class_="Box-sc-g0xbh4-0 bBwPjs search-title")
                    print(str(len(results_list)) + " results found in " + search)

                    for result in results_list:
                        a = result.find('a')
                        title = a.text
                        link = 'https://github.com' + a.get('href')
                        worksheet.write(scrap.row, 0, title)
                        worksheet.write(scrap.row, 1, link)
                        scrap.row += 1
                        scrap.nbr_results += 1
                    scrap.page += 1

            except TimeoutException:
                # No results or last page reached.
                print("No result in " + search)
                scrap.is_results = False
                
                
    def sub_search():
        # Adapt ranges of number of comments to obtain sub_searches with less than 1000 results
        ranges = [(0,1), (2,5), (6, 10), (11, 10000)]
        for range in ranges:
            scrap.page = 1
            scrap.is_results = True
            search(range)
    
    search()
         
    return scrap.nbr_results


date = date.today().strftime("%d-%m-%Y")
file_name = 'NISQBugs_'+ date + '.xlsx'
workbook = xlsxwriter.Workbook(file_name)
bold = workbook.add_format({'bold': True})
results = {}

for query in QUERIES:
    nbr_results = scrap(query)
    results[query] = nbr_results

worksheet = workbook.add_worksheet('Results')
worksheet.write('A1', 'Query', bold)
worksheet.write('B1', 'Number of results', bold)
worksheet.set_column('A:A', 20)
worksheet.set_column('B:B', 20)

for row_number, (query, number_results) in enumerate(results.items(), start=1):
        worksheet.write(row_number, 0, query)
        worksheet.write(row_number, 1, number_results)   
        
workbook.close()

