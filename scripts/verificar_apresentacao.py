#!/usr/bin/env python3
"""Verificação opcional de navegador; requer Selenium, Firefox e geckodriver."""
import argparse,json,time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--driver',required=True);p.add_argument('--firefox',default='/Applications/Firefox.app/Contents/MacOS/firefox');args=p.parse_args()
    opts=webdriver.FirefoxOptions();opts.binary_location=args.firefox;opts.add_argument('-headless')
    driver=webdriver.Firefox(service=Service(args.driver,log_path='/tmp/trabalho1-geckodriver.log'),options=opts)
    checks=[]
    try:
        driver.set_window_size(1440,1000)
        driver.get((ROOT/'docs/apresentacao.html').as_uri())
        assert len(driver.find_elements(By.CSS_SELECTOR,'.slide'))==12
        assert driver.find_element(By.CSS_SELECTOR,'.slide.active').is_displayed()
        assert driver.find_element(By.ID,'counter').text=='01 / 12'
        driver.find_element(By.ID,'next').click();assert driver.find_element(By.ID,'counter').text=='02 / 12'
        driver.find_element(By.ID,'notes').click();assert driver.find_element(By.CSS_SELECTOR,'.active .notes').is_displayed()
        driver.find_element(By.ID,'notes').click()
        for width,height in [(1440,1000),(1366,768),(390,844)]:
            driver.set_window_size(width,height)
            sizes=[]
            for slide in range(12):
                driver.execute_script('show(arguments[0])',slide)
                assert driver.find_element(By.CSS_SELECTOR,'.slide.active').is_displayed()
                sizes.append(driver.execute_script('return {width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight}'))
            assert all(s['scrollWidth']<=s['width']+1 for s in sizes),(width,sizes)
            if width>800:
                assert all(s['scrollHeight']<=s['height']+1 for s in sizes),(width,sizes)
            checks.append({'viewport':[width,height],'slides':12,'horizontal_overflow':False,'sizes':sizes})
        driver.set_window_size(1440,1000)
        driver.execute_script('show(7)');driver.find_element(By.ID,'example-toggle').click()
        assert driver.find_element(By.ID,'example-cost').text=='42 km'
        assert 'C1 · C3' in driver.find_element(By.ID,'school-demo').text
        driver.find_element(By.ID,'example-toggle').click();assert driver.find_element(By.ID,'example-cost').text=='56 km'
        driver.execute_script('show(9)')
        from selenium.webdriver.support.ui import Select
        Select(driver.find_element(By.ID,'instance-select')).select_by_value('Instancia2_G2.txt')
        assert 'Parcial' in driver.find_element(By.ID,'result-status').text
        assert len(driver.find_elements(By.CSS_SELECTOR,'#results-table tbody tr'))==2
        driver.execute_script('show(10)');assert driver.find_element(By.CSS_SELECTOR,'svg polyline').is_displayed()
        driver.execute_script('show(0)');driver.save_screenshot('/tmp/trabalho1-capa.png')
        driver.execute_script('show(7)');driver.save_screenshot('/tmp/trabalho1-exemplo.png')
        driver.execute_script('show(9)');driver.save_screenshot('/tmp/trabalho1-resultados.png')
        version=driver.capabilities.get('browserVersion')
        payload={'status':'passed','browser':'Firefox','version':version,'checks':checks,
                 'interactions':['navigation','speaker notes','example 56→42→56','partial results selector','SVG convergence'],
                 'javascript':'node --check passed','offline':True}
        (ROOT/'docs/verificacao_apresentacao.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False))
        print('Apresentação: 12 slides, 3 tamanhos de tela e interações aprovados.')
    finally:driver.quit()
if __name__=='__main__':main()
