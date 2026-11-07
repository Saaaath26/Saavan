import pytest
from openjarvis.saavan.reviewer import review
class Engine:
    engine_id='test'
    def __init__(self,replies):self.replies=iter(replies)
    def generate(self,*args,**kwargs):return {'content':next(self.replies),'usage':{}}

def test_review_requires_source_evidence():
    engine=Engine(['Action: read_selected_source\nAction Input: {}','Final Answer: Line 1 divides by zero.'])
    result=review({'source':'1: print(1/0)','goal':'Find bugs'},engine)
    assert result['source_reads']==2 and 'Line 1' in result['draft']

def test_source_is_supplied_even_without_model_tool_call():
    class Capture(Engine):
        def generate(self,messages,**kwargs):
            assert '1: x=1' in messages[-1].content
            return super().generate(messages,**kwargs)
    result=review({'source':'1: x=1','goal':'Review'},Capture(['Final Answer: Looks good.']))
    assert result['source_reads']==1

def test_unknown_tool_cannot_execute():
    engine=Engine(['Action: shell_exec\nAction Input: {"command":"echo danger"}']*4)
    with pytest.raises(ValueError):
        review({'source':'1: x=1','goal':'Review'},engine)

@pytest.mark.parametrize('host',['https://example.com','http://127.0.0.1@evil.com','http://127.0.0.1/path'])
def test_only_local_provider(host):
    with pytest.raises(ValueError,match='local Ollama'):
        review({'source':'1: x=1','goal':'Review','host':host},Engine([]))
