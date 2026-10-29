#!/usr/bin/env python3
"""Verificação opcional de navegador; requer Selenium, Firefox e geckodriver."""
import argparse,base64,json,re,subprocess,tempfile
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.print_page_options import PrintOptions
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--driver',required=True);p.add_argument('--firefox',default='/Applications/Firefox.app/Contents/MacOS/firefox');p.add_argument('--export-pdf',action='store_true');args=p.parse_args()
    source=(ROOT/'docs/apresentacao.html').read_text()
    script=re.search(r'<script>(.*?)</script>',source,re.S)[1]
    subprocess.run(['node','--check'],input=script,text=True,check=True)
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
        assert 'K=1: parcial (13 não alocados)' in driver.find_element(By.ID,'result-status').text
        assert 'K=2: completa' in driver.find_element(By.ID,'result-status').text
        assert len(driver.find_elements(By.CSS_SELECTOR,'#results-table tbody tr'))==4
        assert 'Inicial (média)' in driver.find_element(By.ID,'results-table').text
        assert '±' in driver.find_element(By.ID,'results-table').text
        assert 'K=2 TABU' in driver.find_element(By.ID,'precheck-detail').text
        driver.execute_script('show(10)');assert driver.find_element(By.CSS_SELECTOR,'svg polyline').is_displayed()
        curve=driver.find_element(By.CSS_SELECTOR,'svg polyline').get_attribute('points')
        Select(driver.find_element(By.ID,'curve-k-select')).select_by_value('2')
        assert driver.find_element(By.ID,'curve-k-label').text=='K=2'
        assert driver.find_element(By.CSS_SELECTOR,'svg polyline').get_attribute('points')!=curve
        Select(driver.find_element(By.ID,'curve-k-select')).select_by_value('1')
        driver.execute_script('show(0)');driver.save_screenshot('/tmp/trabalho1-capa.png')
        driver.execute_script('show(7)');driver.save_screenshot('/tmp/trabalho1-exemplo.png')
        driver.execute_script('show(9)');driver.save_screenshot('/tmp/trabalho1-resultados.png')
        # Download targets must remain self-contained when the HTML is moved alone.
        for link,target in [('#report-download','docs/relatorio.pdf'),
                            ('a[download="final_resumo.csv"]','resultados/final_resumo.csv')]:
            href=driver.find_element(By.CSS_SELECTOR,link).get_attribute('href')
            assert href.startswith('data:')
            assert base64.b64decode(href.split(',',1)[1])==(ROOT/target).read_bytes()
        with tempfile.TemporaryDirectory(prefix='trabalho1-slides-') as tmp:
            moved=Path(tmp)/'slides.html';moved.write_text(source)
            driver.get(moved.as_uri())
            driver.execute_script('show(11)')
            assert driver.find_element(By.ID,'report-download').get_attribute('href').startswith('data:application/pdf;base64,')
            assert len(driver.find_elements(By.CSS_SELECTOR,'#results-table tbody tr'))==4
        driver.get((ROOT/'docs/apresentacao.html').as_uri())
        pdf_pages=None
        if args.export_pdf:
            options=PrintOptions();options.orientation='landscape'
            options.page_width=29.7;options.page_height=21
            options.margin_top=1.2;options.margin_bottom=1.2
            options.margin_left=1.2;options.margin_right=1.2
            options.background=True;options.shrink_to_fit=False
            payload=driver.print_page(options)
            pdf_path=ROOT/'docs/apresentacao.pdf'
            pdf_path.write_bytes(base64.b64decode(payload))
            import fitz
            with fitz.open(pdf_path) as pdf:
                assert len(pdf)==12, f'PDF tem {len(pdf)} páginas, esperadas 12'
                assert all(page.get_text().strip() for page in pdf)
                assert 'I2 G2' in pdf[9].get_text() and 'K=2' in pdf[9].get_text()
                assert all(label in pdf[9].get_text() for label in ['Inicial (média)','Final (média)','Total (s)'])
                assert 'github.com/brunokeil/Trabalho_Inteligencia_Computacional' in pdf[11].get_text()
                pdf_pages=len(pdf)
        version=driver.capabilities.get('browserVersion')
        payload={'status':'passed','browser':'Firefox','version':version,'checks':checks,
                 'interactions':['navigation','speaker notes','example 56→42→56','K=1/K=2 results selector',
                                 'SVG convergence for both K','embedded PDF/CSV match current files','HTML moved alone'],
                 'javascript':'node --check passed','offline':True,'pdf_pages':pdf_pages}
        (ROOT/'docs/verificacao_apresentacao.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False))
        print('Apresentação: 12 slides, 3 tamanhos de tela, ambos os valores de K e downloads offline aprovados.',flush=True)
        if pdf_pages:print(f'PDF exportado e verificado: {pdf_pages} páginas.',flush=True)
    finally:driver.quit()
if __name__=='__main__':main()
