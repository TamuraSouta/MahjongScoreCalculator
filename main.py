import streamlit as st
import os
import pickle
from datetime import datetime
import random

# データを保存・読み込むためのファイルパス
FILE_PATH = 'mahjong_scores.pkl'
PENDING_PATH = 'pending_scores.pkl'

# 管理者のユーザー名とパスワード
ADMIN_USERNAME = ''
ADMIN_PASSWORD = ''

player_names = [
    "トト丸", "mion", "すだち油", "たまやん", "つき", "とまと", 
    "黒くん(人工芝)", "いちまる", "すじこ", "たむら","カジキ侍",
    "魚の燻製", "むっかー","ティアラ","蒼瀬","国士無双","歩",
    "海てつお","神城"
]

def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def save_data(data, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
st.title('麻雀アプリ')

# データのロード
if 'scores' not in st.session_state:
    st.session_state['scores'] = load_data(FILE_PATH)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 管理者ページ
if st.session_state['logged_in']:
    st.sidebar.title("管理者ページ")
    
    # データのロード
    scores = load_data(FILE_PATH)
    pending_scores = load_data(PENDING_PATH)

    game_ids = list(pending_scores.keys())

    # プレイヤー選択
    player_names = list(scores.keys())
    selected_player = st.sidebar.selectbox("プレイヤーを選択", player_names)

    # 現在の点数を表示
    current_scores = scores.get(selected_player, [])
    st.sidebar.text(f"現在の点数: {sum(current_scores)}")

    # 新しい点数の入力
    new_score = st.sidebar.number_input("調整値入力", value=0)

    # 更新ボタン
    if st.sidebar.button('点数を調整'):
        if selected_player in scores:
            scores[selected_player].append(new_score)
            save_data(scores, FILE_PATH)
            st.sidebar.success(f"{selected_player}の点数を更新しました。")
            st.experimental_rerun()
    # 選択した試合IDのスコア一覧と操作
    selected_game_id = st.sidebar.selectbox("試合IDを選択", game_ids)
    if selected_game_id:
        game_scores = pending_scores[selected_game_id]

        # 各プレイヤーのスコアと個別の承認または却下オプション
        for player, score_details in list(game_scores.items()):
            input_score, adjusted_score, is_approved = score_details
            if not is_approved:
                st.sidebar.markdown(f"**{player}: {input_score}点**")

        # 全てのスコアを一括で承認
        if st.sidebar.button('承認'):
            for player, score_details in game_scores.items():
                input_score, adjusted_score, is_approved = score_details
                if not is_approved:
                    game_scores[player] = [input_score, adjusted_score, True]
                    if player not in scores:
                        scores[player] = []
                    scores[player].append(adjusted_score)
            del pending_scores[selected_game_id]  # 承認後、この試合IDを削除
            game_ids.remove(selected_game_id)  # リストからも削除
            save_data(pending_scores, PENDING_PATH)
            save_data(scores, FILE_PATH)
            st.experimental_rerun()
        # 全てのスコアを一括で却下
        if st.sidebar.button(f'却下'):
            del pending_scores[selected_game_id]  # 却下後、この試合IDを削除
            game_ids.remove(selected_game_id)  # リストからも削除
            save_data(pending_scores, PENDING_PATH)
            st.experimental_rerun()
        
else:
    st.sidebar.title("ログイン")
    username = st.sidebar.text_input("ユーザー名")
    password = st.sidebar.text_input("パスワード", type='password')
    if st.sidebar.button('ログイン'):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state['logged_in'] = True
            st.experimental_rerun()
        else:
            st.sidebar.error("ユーザー名またはパスワードが間違っています。")

# プレイヤーの選択と点数入力
selected_players = st.multiselect('プレイヤーを選択してください（3人または4人）', player_names)
game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M')}_{random.randint(1000, 9999)}"

# スコア入力の初期化と表示
for player in selected_players:
    if player not in st.session_state:
        st.session_state[player] = 0
    st.session_state[player] = st.number_input(f'{player}の点数', key=f'score_{player}', value=st.session_state[player])

# 点数申請の制御
if len(selected_players) == 3 or len(selected_players) == 4:
    if st.button('点数を申請'):
        initial_points = 35000 if len(selected_players) == 3 else 25000
        pending_scores = load_data(PENDING_PATH)
        if game_id not in pending_scores:
            pending_scores[game_id] = {}
        total_input_score = 0  # 入力されたスコアの合計値を初期化

        for player in selected_players:
            input_score = st.session_state[player]
            total_input_score += input_score  # 各プレイヤーのスコアを合計に加算

        if total_input_score == 105000 or total_input_score == 100000:
            for player in selected_players:
                input_score = st.session_state[player]
                adjusted_score = input_score - initial_points
                pending_scores[game_id][player] = [input_score, adjusted_score, False]
                st.success(f"試合ID {player} {input_score} の点数申請を受け付けました。")

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
        st.write(f"{idx}位: {player} - 点数: {score}点")  # スコアをそのまま表示

# データのロード
scores = load_data(FILE_PATH)
pending_scores = load_data(PENDING_PATH)

# データ表示
st.write("スコアデータ:", scores)
st.write("承認待ちスコアデータ:", pending_scores)
