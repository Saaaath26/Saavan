import json
import pytest
from openjarvis.saavan.runtime import DesktopRuntime
from openjarvis.saavan.engine import SaavanOllamaEngine as OllamaEngine

@pytest.fixture
def runtime(tmp_path,monkeypatch):
    monkeypatch.setenv('OPENJARVIS_HOME',str(tmp_path))
    monkeypatch.setattr(OllamaEngine,'health',lambda self:True)
    monkeypatch.setattr(OllamaEngine,'generate',lambda *a,**k:{'content':'{"ready":true}','usage':{}})
    obj=DesktopRuntime(tmp_path,'http://127.0.0.1:11434','test')
    yield obj
    obj.close()

def test_native_components_initialized(runtime):
    assert all(runtime.describe()['components'].values())
    assert set(runtime.describe()['tools'])=={'think','calculator','retrieval'}
    assert not runtime.system.config.analytics.enabled
    assert runtime.system.capability_policy is not None

def test_index_replace_search_forget(runtime):
    runtime.index('sample.md','Zephyr milestone is Tuesday. Other text.')
    assert runtime.search('Zephyr')[0]['source']=='sample.md'
    runtime.index('sample.md','Orchid milestone is Wednesday.')
    assert not runtime.search('Zephyr')
    assert runtime.search('Orchid')
    runtime.forget('sample.md')
    assert not runtime.search('Orchid')

def test_structured_generation(runtime):
    assert json.loads(runtime.generate('JSON please',structured=True))=={'ready':True}

def test_agent_returns_final_only_and_evidence(runtime,monkeypatch):
    monkeypatch.setattr(runtime.system,'ask',lambda *a,**k:{'content':'Thought: internal draft\nFinal Answer: 391','metadata':{},'tool_results':[{'tool_name':'calculator','success':True}],'turns':2})
    result=runtime.ask('Calculate')
    assert result['answer']=='391'
    assert result['tools']==[{'name':'calculator','success':True}]

def test_agent_incomplete_result_rejected(runtime,monkeypatch):
    monkeypatch.setattr(runtime.system,'ask',lambda *a,**k:{'content':'Partial','metadata':{'max_turns_exceeded':True}})
    with pytest.raises(ValueError):runtime.ask('Test')


def test_structured_adapter_preserves_generate_protocol():
    import httpx
    from openjarvis.saavan.engine import SaavanOllamaEngine
    from openjarvis.core.types import Message,Role
    engine=SaavanOllamaEngine()
    engine._client.close()
    def respond(request):
        assert request.url.path=='/api/generate'
        body=json.loads(request.content)
        assert body['system']=='JSON only' and body['prompt']=='user task'
        assert body['format']=='json'
        return httpx.Response(200,json={'response':'{"ok":true}','prompt_eval_count':2,'eval_count':3})
    engine._client=httpx.Client(base_url='http://localhost:11434',transport=httpx.MockTransport(respond))
    try:
        data=engine.generate([Message(role=Role.SYSTEM,content='JSON only'),Message(role=Role.USER,content='user task')],model='test',response_format={'type':'json_object'})
        assert data['usage']['total_tokens']==5
    finally:engine._client.close()
