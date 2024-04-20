import streamlit as st
import os
import pickle

# データを保存・読み込むためのファイルパス
FILE_PATH = 'mahjong_scores.pkl'
PENDING_PATH = 'pending_scores.pkl'

# 管理者のユーザー名とパスワード
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def save_data(data, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)

st.title('麻雀点数記録アプリ')

# データのロード
if 'scores' not in st.session_state:
    st.session_state['scores'] = load_data(FILE_PATH)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 管理者ページ
if st.session_state['logged_in']:
    st.sidebar.title("管理者ページ")
    pending_scores = load_data(PENDING_PATH)

    to_remove = []
    for player, score_details in list(pending_scores.items()):
        score, is_approved = score_details
        if not is_approved:
            col1, col2 = st.sidebar.columns(2)
            if col1.button(f"承認 {player}", key=f"approve_{player}"):
                pending_scores[player] = [score, True]
                if player not in st.session_state['scores']:
                    st.session_state['scores'][player] = []
                st.session_state['scores'][player].append(score)
                save_data(pending_scores, PENDING_PATH)
                save_data(st.session_state['scores'], FILE_PATH)
                st.sidebar.success(f"{player}の点数を追加しました")
                st.experimental_rerun()
            if col2.button(f"却下 {player}", key=f"reject_{player}"):
                to_remove.append(player)
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
player_names = [f'プレイヤー{i+1}' for i in range(20)]
selected_players = st.multiselect('プレイヤーを選択してください（3人または4人）', player_names)

# スコア入力の初期化と表示
for player in selected_players:
    if player not in st.session_state:
        st.session_state[player] = 0
    st.session_state[player] = st.number_input(f'{player}の点数', key=f'score_{player}', value=st.session_state[player])

if st.button('点数を申請'):
    initial_points = 35000 if len(selected_players) == 3 else 25000
    pending_scores = load_data(PENDING_PATH)
    for player in selected_players:
        input_score = st.session_state[player]
        adjusted_score = input_score - initial_points
        pending_scores[player] = [adjusted_score, False]
        save_data(pending_scores, PENDING_PATH)
        st.success(f"{player}の{adjusted_score}点の申請を受け付けました")


# 順位の表示
if st.button('順位を表示'):
    total_scores = {player: sum(scores) for player, scores in st.session_state['scores'].items()}
    adjusted_scores = {player: total // 1000 for player, total in total_scores.items()}
    sorted_scores = dict(sorted(adjusted_scores.items(), key=lambda item: item[1], reverse=True))
    st.subheader('順位表')
    for idx, (player, score) in enumerate(sorted_scores.items(), 1):
        st.write(f"{idx}位: {player} - 点数: {score}点")
