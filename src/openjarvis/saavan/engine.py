"""Ollama adapter preserving Saavan's established JSON-generation protocol."""
from openjarvis.engine.ollama import OllamaEngine

class SaavanOllamaEngine(OllamaEngine):
    def generate(self,messages,*,model,temperature=.2,max_tokens=2048,**kwargs):
        if kwargs.get('response_format') is None:
            return super().generate(messages,model=model,temperature=temperature,max_tokens=max_tokens,**kwargs)
        # Source edits and plan schemas already use Ollama's generate API. Keep
        # its prompt framing while sharing OpenJarvis scanning/audit/telemetry.
        system='\n'.join(m.content for m in messages if str(getattr(m.role,'value',m.role))=='system')
        user=[m.content for m in messages if str(getattr(m.role,'value',m.role))!='system']
        response=self._client.post('/api/generate',json={'model':model,'system':system,'prompt':'\n'.join(user),
            'format':'json','stream':False,'options':{'temperature':temperature,'num_predict':max_tokens}})
        response.raise_for_status();data=response.json()
        prompt=data.get('prompt_eval_count',0);completion=data.get('eval_count',0)
        return {'content':data.get('response',''),'usage':{'prompt_tokens':prompt,'completion_tokens':completion,'total_tokens':prompt+completion},'model':model,'finish_reason':'stop'}
