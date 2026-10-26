import copy,json,subprocess,tempfile,unittest,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validar import validate
BASE='''NUM_CANDIDATOS: 2
NUM_ESCOLAS: 2
# CANDIDATOS
C1827, 36088-211, M1, -21, -43
C3, 36088-212, M2, -21, -43
# ESCOLAS
E9, 36088-213, -21, -43, 2, 1; 1
E2, 36088-214, -21, -43, 1, 2
# MATRIZ_DISTANCIAS
1.0001, 2.0002
3.0003, 4.0004
'''
class Integration(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def run_case(self,txt,args=()):
        inp=self.root/'in.txt';inp.write_text(txt);return subprocess.run([os.environ.get('DCC136_TEST_BIN',str(ROOT/'alocacao')),'--instancia',str(inp),'--viabilidade-script',str(ROOT/'scripts/viabilidade.py'),*args],capture_output=True,text=True,timeout=30)
    def test_bad_parser(self):
        for text in ['',BASE.replace('NUM_CANDIDATOS: 2','NUM_CANDIDATOS: 3'),BASE.replace('2, 1; 1','3, 1; 1'),BASE.replace('1.0001, 2.0002','1.0001'),BASE.replace('1.0001','oops'),BASE.replace('1.0001','-1'),BASE+'7,8\n',BASE.replace('C3,','C1827,')]:
            with self.subTest(text=text):
                r=self.run_case(text,['--tipos-por-escola','1']);self.assertEqual(r.returncode,1,r.stderr);self.assertIn('Erro:',r.stderr)
    def test_ids_whitespace_and_validator_rejection(self):
        out=self.root/'result.json';r=self.run_case('\n  '+BASE.replace('# CANDIDATOS','# comentario')+'\n',['--tipos-por-escola','2','--saida',str(out)])
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(validate(out),2)
        data=json.loads(out.read_text());self.assertEqual(data['candidateIds'],['C1827','C3']);self.assertEqual(data['schoolIds'],['E9','E2'])
        bad=copy.deepcopy(data);bad['runs'][0]['final']['distance']+=1;out.write_text(json.dumps(bad))
        with self.assertRaises(AssertionError):validate(out)
    def test_determinism_both_methods(self):
        for method in ('vnd','tabu'):
            documents=[]
            for rep in range(2):
                out=self.root/f'{method}{rep}.json';r=self.run_case(BASE,['--tipos-por-escola','1','--metodo',method,'--alpha','.3','--seed','42','--saida',str(out),'--max-iter','30'])
                self.assertEqual(r.returncode,0,r.stderr);validate(out);documents.append(json.loads(out.read_text())['runs'][0])
            for key in ('initial','final','convergence','evaluations','moves','iterations'):self.assertEqual(documents[0][key],documents[1][key])
    def test_exact_decimal_export(self):
        text="NUM_CANDIDATOS: 1\nNUM_ESCOLAS: 1\nC1, 36000-000, M1, 0, 0\nE1, 36000-001, 0, 0, 1, 1\n8982.1431\n"
        out=self.root/'decimal.json';r=self.run_case(text,['--tipos-por-escola','1','--saida',str(out)])
        self.assertEqual(r.returncode,0,r.stderr);validate(out)
    def test_bad_cli(self):
        for args in [(),('--tipos-por-escola','3'),('--tipos-por-escola','1','--alpha','nan'),('--tipos-por-escola','1','--alpha','1.1'),('--tipos-por-escola','1','--runs','0'),('--tipos-por-escola','1','--ls','wrong'),('--tipos-por-escola','1','--tmin','10','--tmax','2')]:
            r=self.run_case(BASE,args);self.assertEqual(r.returncode,1,r.stderr)
    def test_output_extensions_cannot_overwrite_input(self):
        inp=self.root/'data.csv';inp.write_text(BASE)
        result=subprocess.run([os.environ.get('DCC136_TEST_BIN',str(ROOT/'alocacao')),
            '--instancia',str(inp),'--tipos-por-escola','1',
            '--saida',str(self.root/'data.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertIn('sobrescrever',result.stderr)
        self.assertEqual(inp.read_text(),BASE)
if __name__=='__main__':unittest.main()
