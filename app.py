from pathlib import Path
import math,json,textwrap
import pandas as pd,numpy as np,streamlit as st,plotly.graph_objects as go
P=Path(__file__).parent/'data';L=pd.read_csv(P/'locations.csv');D=pd.read_csv(P/'dimensions.csv');Q=pd.read_csv(P/'quality_report.csv');K=D.dimension_key.tolist();LAB=dict(zip(D.dimension_key,D.label));THEMES=D.groupby('theme').dimension_key.apply(list).to_dict()
PRESETS={'Stephen & Julie':{'household':'Retired couple','budget':'£1m–£2m','horizon':'3–8 years','notes':'Restaurants, walking, culture, travel and staying close to family. Character without isolation.','weights':{'Home & value':6,'Everyday life':8,'Connections':10,'Outdoors':9,'Culture & community':9,'Character & future':8}},'Active coastal next chapter':{'household':'Retired couple','budget':'£750k–£1m','horizon':'0–3 years','notes':'Coast, walking, community and a lively year-round centre.','weights':{'Home & value':6,'Everyday life':7,'Connections':6,'Outdoors':10,'Culture & community':8,'Character & future':9}},'Connected culture':{'household':'Couple','budget':'£1m–£2m','horizon':'3–8 years','notes':'Culture, food, learning and straightforward access to family.','weights':{'Home & value':5,'Everyday life':8,'Connections':10,'Outdoors':6,'Culture & community':10,'Character & future':8}}}
st.set_page_config(page_title='Location Lifestyle AI V8',page_icon='🧭',layout='wide');st.markdown('''<style>.block-container{padding-top:1rem}.hero{padding:1.15rem 1.5rem;border-radius:18px;background:linear-gradient(120deg,#10372b,#527c67);color:white}.brief{padding:.9rem 1.1rem;border-left:6px solid #dba641;background:#f7faf8;border-radius:12px}.stTabs [data-baseweb="tab"]{font-size:.9rem}</style>''',unsafe_allow_html=True)
if 'profile' not in st.session_state:st.session_state.profile=json.loads(json.dumps(PRESETS['Stephen & Julie']))
if 'network' not in st.session_state:st.session_state.network=pd.DataFrame([{'Remove':False,'Place':'St Albans','Category':'Family','Importance':10,'Visits/month':4.0},{'Remove':False,'Place':'Marlow','Category':'Home / friends','Importance':7,'Visits/month':2.0}])
if 'floor' not in st.session_state:st.session_state.floor=58
def miles(a,b,c,d):
 z=math.sin(math.radians(c-a)/2)**2+math.cos(math.radians(a))*math.cos(math.radians(c))*math.sin(math.radians(d-b)/2)**2;return 7917.6*math.asin(math.sqrt(z))
def journeys(r):
 rows=[]
 for _,n in st.session_state.network.iterrows():
  h=L[L.name==n.Place]
  if h.empty:continue
  mi=miles(r.latitude,r.longitude,h.iloc[0].latitude,h.iloc[0].longitude);road=10+60*mi/35;pt=30+60*mi/45;v=float(n['Visits/month']);rows.append({'Place':n.Place,'Category':n.Category,'Importance':float(n.Importance),'Visits/month':v,'Miles':mi,'Road minutes':road,'Public transport minutes':pt,'Road monthly hours':2*road*v/60,'Public transport monthly hours':2*pt*v/60,'Road node score':max(0,100-road/3),'lat':h.iloc[0].latitude,'lon':h.iloc[0].longitude})
 return pd.DataFrame(rows)
def score():
 ww={k:st.session_state.profile['weights'][t] for t,ks in THEMES.items() for k in ks};w=np.array([ww[k] for k in K]);o=L.copy();o['Lifestyle']=o[K].to_numpy()@w/(10*w.sum())*100
 def ns(r):
  z=journeys(r);return 75 if z.empty else float(np.average(z['Road node score'],weights=z.Importance*np.maximum(z['Visits/month'],.25)))
 o['Life Network']=o.apply(ns,axis=1);o['Balanced']=.55*o.Lifestyle+.45*o['Life Network'];return o.sort_values(['Balanced','importance_rank'],ascending=[False,True]),ww
def gauge(v,title,key):
 title='<br>'.join(textwrap.wrap(title,15));f=go.Figure(go.Indicator(mode='gauge+number',value=v,title={'text':title,'font':{'size':11}},number={'font':{'size':21}},gauge={'axis':{'range':[0,100],'tickfont':{'size':7}},'bar':{'color':'#2d6a51'},'steps':[{'range':[0,45],'color':'#f2d0c9'},{'range':[45,70],'color':'#f1dfae'},{'range':[70,100],'color':'#acd1bd'}]}));f.update_layout(height=138,margin=dict(l=7,r=7,t=38,b=2));st.plotly_chart(f,use_container_width=True,key=key)
def hhmm(m):return f'{int(m//60)}h {int(round(m%60)):02d}m' if m>=60 else f'{int(round(m))}m'
def jmap(r,z,mode):
 tm='Road minutes' if mode=='Road' else 'Public transport minutes';bm='Road monthly hours' if mode=='Road' else 'Public transport monthly hours';f=go.Figure()
 for _,n in z.iterrows():
  m=n[tm];c='#27935a' if m<=60 else '#d99c2f' if m<=120 else '#c74840';lab=f"{n.Place}<br>{n.Miles:.0f} miles<br>{mode}: {hhmm(m)}<br>{n[bm]:.1f} h/month";f.add_trace(go.Scattergeo(lon=[r.longitude,n.lon],lat=[r.latitude,n.lat],mode='lines',line=dict(color=c,width=2+3*n.Importance/10),hovertext=[lab,lab],hoverinfo='text',showlegend=False));f.add_trace(go.Scattergeo(lon=[n.lon],lat=[n.lat],mode='markers+text',text=[n.Place],textposition='top center',marker=dict(size=10+n.Importance,color=c,line=dict(width=1,color='white')),hovertext=lab,hoverinfo='text',showlegend=False))
 f.add_trace(go.Scattergeo(lon=[r.longitude],lat=[r.latitude],mode='markers+text',text=[r['name']],textposition='top center',marker=dict(size=25,color='#153d31',symbol='star'),showlegend=False));f.update_geos(scope='europe',fitbounds='locations',showland=True,landcolor='#eef3ef',showocean=True,oceancolor='#e5f0f3',showcoastlines=True);f.update_layout(height=620,margin=dict(l=0,r=0,t=10,b=0));return f
st.markdown('<div class="hero"><h1>🧭 Location Lifestyle AI V8</h1><p>Recommended places, household fit and the monthly cost of staying connected.</p></div>',unsafe_allow_html=True)
with st.sidebar:
 p=st.session_state.profile;st.header('Household profile');preset=st.selectbox('Preset',PRESETS)
 if st.button('Load preset',use_container_width=True):st.session_state.profile=json.loads(json.dumps(PRESETS[preset]));st.rerun()
 p['household']=st.selectbox('Household',['Single','Couple','Family','Retired couple'],index=['Single','Couple','Family','Retired couple'].index(p['household']));p['budget']=st.selectbox('Budget',['Under £500k','£500k–£750k','£750k–£1m','£1m–£2m','£2m+'],index=['Under £500k','£500k–£750k','£750k–£1m','£1m–£2m','£2m+'].index(p['budget']));p['horizon']=st.selectbox('Horizon',['0–3 years','3–8 years','8–15 years'],index=['0–3 years','3–8 years','8–15 years'].index(p['horizon']));p['notes']=st.text_area('What matters',p['notes'],height=85);current=st.selectbox('Current location',L.name,index=int(L.index[L.name=='Marlow'][0]))
 for t in THEMES:p['weights'][t]=st.slider(t,0,10,p['weights'][t],key='w'+t)
 payload={'profile':p,'current':current,'network_floor':st.session_state.floor,'life_network':st.session_state.network.to_dict('records')};st.download_button('Download profile',json.dumps(payload,indent=2),'profile_v8.json','application/json',use_container_width=True);up=st.file_uploader('Import profile',type='json')
 if up and st.button('Apply imported profile'):
  x=json.load(up);st.session_state.profile=x['profile'];st.session_state.floor=x.get('network_floor',58);st.session_state.network=pd.DataFrame(x.get('life_network',[]));st.rerun()
out,W=score();base=out[out.name==current].iloc[0];basez=journeys(base);baseh=basez['Road monthly hours'].sum();focus=sorted(p['weights'],key=p['weights'].get,reverse=True)[:3]
st.markdown(f'<div class="brief"><b>{p["household"]}, {p["budget"]}, {p["horizon"]}:</b> prioritising {focus[0].lower()}, {focus[1].lower()} and {focus[2].lower()}. Recommendations first apply the Life Network threshold, then balance lifestyle and network fit.</div>',unsafe_allow_html=True)
tabs=st.tabs(['Recommended places','Journey Map','Life Network editor','Dashboard','Travel table','Compare','Place conversation','Data quality'])
with tabs[0]:
 c1,c2,c3=st.columns(3);floor=c1.slider('Minimum Life Network',0,100,st.session_state.floor);st.session_state.floor=floor;n=c2.slider('Shortlist length',5,25,12);regions=c3.multiselect('Regions',sorted(L.region.unique()),default=sorted(L.region.unique()));pool=out[(out.name!=current)&out.region.isin(regions)&(out['Life Network']>=floor)].copy();x=pool.head(n);x['Road monthly h']=x.apply(lambda r:journeys(r)['Road monthly hours'].sum(),axis=1);x['Δ vs current h']=x['Road monthly h']-baseh
 st.caption(f'{len(pool)} places clear the Life Network gate.');st.dataframe(x[['name','county_area','region','Lifestyle','Life Network','Balanced','Road monthly h','Δ vs current h']].style.format({'Lifestyle':'{:.1f}','Life Network':'{:.1f}','Balanced':'{:.1f}','Road monthly h':'{:.1f}','Δ vs current h':'{:+.1f}'}),hide_index=True,use_container_width=True);st.scatter_chart(x,x='Lifestyle',y='Life Network',color='region',size='Balanced')
with tabs[1]:
 a,b=st.columns([2,1]);cn=a.selectbox('Candidate',out.name);mode=b.radio('View',['Road','Public transport','Both']);r=out[out.name==cn].iloc[0];z=journeys(r)
 if mode=='Both':
  c,d=st.columns(2);c.plotly_chart(jmap(r,z,'Road'),use_container_width=True);d.plotly_chart(jmap(r,z,'Public transport'),use_container_width=True)
 else:st.plotly_chart(jmap(r,z,mode),use_container_width=True)
 st.caption('Candidate shown as a star. Green ≤60 min, amber 61–120, red >120. Lines are direct geographic connectors, not routed roads or railway lines. Hover shows miles, estimated time and monthly burden.')
with tabs[2]:
 e=st.data_editor(st.session_state.network,num_rows='dynamic',hide_index=True,use_container_width=True,column_config={'Remove':st.column_config.CheckboxColumn('Remove'),'Place':st.column_config.SelectboxColumn(options=L.name.tolist()),'Category':st.column_config.SelectboxColumn(options=['Family','Friends','Home / friends','Travel','Healthcare','Culture','Other']),'Importance':st.column_config.NumberColumn(min_value=1,max_value=10),'Visits/month':st.column_config.NumberColumn(min_value=.1,max_value=30.,step=.5)})
 if st.button('Apply network changes',type='primary'):
  e=e[~e.Remove.fillna(False)].copy();e['Remove']=False;st.session_state.network=e;st.rerun()
with tabs[3]:
 a,b,c,d=st.columns(4);a.metric('Catalogue',len(L));b.metric('Network nodes',len(st.session_state.network));c.metric('Current lifestyle',f'{base.Lifestyle:.0f}');d.metric('Current network',f"{base['Life Network']:.0f}");cs=st.columns(6)
 for i,(t,v) in enumerate(p['weights'].items()):
  with cs[i]:gauge(v*10,t,'g'+t)
with tabs[4]:
 cn=st.selectbox('Candidate',out.name,key='travel');st.dataframe(journeys(out[out.name==cn].iloc[0]),hide_index=True,use_container_width=True)
with tabs[5]:
 choices=st.multiselect('Compare 2–4',L.name,default=['Marlow','Winchester','Stamford'],max_selections=4)
 if len(choices)>1:
  c=out[out.name.isin(choices)].set_index('name').copy();c['Road monthly h']=[journeys(r)['Road monthly hours'].sum() for _,r in c.iterrows()];c['Public transport monthly h']=[journeys(r)['Public transport monthly hours'].sum() for _,r in c.iterrows()];st.dataframe(c[['Lifestyle','Life Network','Balanced','Road monthly h','Public transport monthly h','county_area','region']].T,use_container_width=True)
with tabs[6]:
 cn=st.selectbox('Discuss',out.name);r=out[out.name==cn].iloc[0];drivers=sorted(K,key=lambda k:r[k]*W[k],reverse=True);z=journeys(r);st.subheader(f"{r['name']} · {r['county_area']} · {r['region']}");st.markdown(f"**{LAB[drivers[0]]}**, **{LAB[drivers[1]]}** and **{LAB[drivers[2]]}** are the strongest model drivers. Road-proxy monthly return travel is **{z['Road monthly hours'].sum():.1f} hours**, **{z['Road monthly hours'].sum()-baseh:+.1f} versus {current}**.\n\n**Profile context:** {p['notes']}")
with tabs[7]:
 a,b,c=st.columns(3);a.metric('Places',len(L));b.metric('Coordinate completeness',f"{L.latitude.notna().mean()*100:.0f}%");c.metric('QA checks passed',int(Q.passed.sum()));st.dataframe(Q,hide_index=True,use_container_width=True);st.dataframe(L[['name','county_area','region','latitude','longitude','coordinate_source','coordinate_status']],hide_index=True,use_container_width=True);st.download_button('Download catalogue',L.to_csv(index=False),'locations_v8.csv','text/csv');st.warning('Travel times are distance-based estimates: road 35 mph plus 10 minutes; public transport 45 mph plus 30 minutes. They are not live routing, traffic or timetables. Lifestyle scores remain seed assessments.')
