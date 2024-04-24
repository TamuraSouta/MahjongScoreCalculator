import streamlit as st
import os
import pickle
from datetime import datetime
import random
import asyncio


# データを保存・読み込むためのファイルパス
FILE_PATH = 'mahjong_scores.pkl'
PENDING_PATH = 'pending_scores.pkl'

# 管理者のユーザー名とパスワード
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

player_names = [
    "トト丸", "mion", "すだち油", "たまやん", "つき", "とまと", 
    "黒くん(人工芝)", "いちまる", "すじこ", "たむら","カジキ侍",
    "魚の燻製", "むっかー","ティアラ","蒼瀬","国士無双","歩",
    "海てつお","神城"
]

@st.cache_data
def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def save_data(data, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)

def handle_score_approval(player, score_details, game_id, pending_scores, scores):
    input_score, adjusted_score, _ = score_details
    scores[player] = scores.get(player, []) + [adjusted_score]
    pending_scores[game_id][player] = [input_score, adjusted_score, True]
    save_data(pending_scores, PENDING_PATH)
    save_data(scores, FILE_PATH)
    st.sidebar.success(f"{player}の点数を追加しました")

def handle_score_rejection(player, game_id, pending_scores):
    del pending_scores[game_id][player]
    save_data(pending_scores, PENDING_PATH)


async def async_load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['data_loaded'] = False

if st.session_state['logged_in'] and not st.session_state['data_loaded']:
    scores_future = asyncio.ensure_future(async_load_data(FILE_PATH))
    pending_scores_future = asyncio.ensure_future(async_load_data(PENDING_PATH))
    st.session_state['scores'], st.session_state['pending_scores'] = await asyncio.gather(scores_future, pending_scores_future)
    st.session_state['data_loaded'] = True


st.title('麻雀アプリ')

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    # 管理者ページ用のデータロード
    if 'scores' not in st.session_state:
        st.session_state['scores'] = load_data(FILE_PATH)
    if 'pending_scores' not in st.session_state:
        st.session_state['pending_scores'] = load_data(PENDING_PATH)
        
    st.sidebar.title("管理者ページ")
    game_ids = list(st.session_state['pending_scores'].keys())
    selected_game_id = st.sidebar.selectbox("試合IDを選択", game_ids)
    
    if selected_game_id:
        game_scores = st.session_state['pending_scores'][selected_game_id]
        scores_text = '\n'.join([f"{player}: {score_details[0]}点" for player, score_details in game_scores.items() if not score_details[2]])
        st.sidebar.text(scores_text)
        
        col1, col2 = st.sidebar.columns(2)
        if col1.button("全て承認"):
            for player, score_details in list(game_scores.items()):
                input_score, adjusted_score, _ = score_details
                st.session_state['scores'][player] = st.session_state['scores'].get(player, []) + [adjusted_score]
                game_scores[player] = [input_score, adjusted_score, True]
            save_data(st.session_state['pending_scores'], PENDING_PATH)
            save_data(st.session_state['scores'], FILE_PATH)
            st.experimental_rerun()
        
        if col2.button("全て却下"):
            st.session_state['pending_scores'].pop(selected_game_id, None)
            save_data(st.session_state['pending_scores'], PENDING_PATH)
            st.experimental_rerun()
else:
    st.sidebar.title("ログイン")
    username = st.sidebar.text_input("ユーザー名")
    password = st.sidebar.text_input("パスワード", type='password')
    if st.sidebar.button('ログイン'):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state['logged_in'] = True
            # ログイン成功時にデータをロード
            st.session_state['scores'] = load_data(FILE_PATH)
            st.session_state['pending_scores'] = load_data(PENDING_PATH)
        else:
            st.sidebar.error("ユーザー名またはパスワードが間違っています。")

# プレイヤーの選択と点数入力
selected_players = st.multiselect('プレイヤーを選択してください（3人または4人）', player_names)
game_id = f"{datetime.now().strftime('%H%M')}_{random.randint(100, 999)}"

# スコア入力の初期化と表示
for player in selected_players:
    st.session_state[player] = st.number_input(f'{player}の点数', key=f'score_{player}', value=st.session_state.get(player, 0))

# 点数申請の制御
if len(selected_players) in [3, 4]:
    if st.button('点数を申請'):
        initial_points = 35000 if len(selected_players) == 3 else 25000
        total_input_score = sum(st.session_state[player] for player in selected_players)
        if total_input_score in [105000, 100000]:
            pending_scores = st.session_state['pending_scores']
            pending_scores[game_id] = {player: [st.session_state[player], st.session_state[player] - initial_points, False] for player in selected_players}
            save_data(pending_scores, PENDING_PATH)
            st.success(f"試合ID {game_id} の点数申請を受け付けました。")
        else:
            st.warning("入力値が正しいか確認してください")
else:
    st.warning('3人または4人のプレイヤーを選択してください。')

# 順位の表示
if st.button('順位を表示'):
    total_scores = {player: sum(scores) for player, scores in st.session_state['scores'].items()}
    sorted_scores = dict(sorted(total_scores.items(), key=lambda item: item[1], reverse=True))
    st.subheader('順位表')
    for idx, (player, score) in enumerate(sorted_scores.items(), 1):
        st.write(f"{idx}位: {player} - 点数: {score // 1000}点")
