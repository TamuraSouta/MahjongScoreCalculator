import streamlit as st
import os
import pickle

# データを保存・読み込むためのファイルパス
FILE_PATH = 'mahjong_scores.pkl'
PENDING_PATH = 'pending_scores.pkl'

# 管理者のユーザー名とパスワード
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

player_names = [
    "トト丸", "mion", "すだち油", "たまやん", "つき", "とまと", 
    "もりもり", "黒くん(人工芝)", "いちまる", "すじこ", "たむら", 
    "魚の燻製", "むっかー"
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

st.title('麻雀大会アプリ')

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

    # スコアの編集
    st.sidebar.subheader("スコアの編集")
    players = list(scores.keys())
    selected_player = st.sidebar.selectbox("プレイヤーを選択", players)
    
    if selected_player:
        # 現在の合計スコアを計算
        current_total_score = sum(scores[selected_player])
        st.sidebar.write(f"現在の合計スコア: {current_total_score}点")
        
        # 新しい合計スコアの入力
        new_total_score = st.sidebar.number_input("新しい合計スコアを入力", value=current_total_score)

        # スコア更新の処理
        if st.sidebar.button("合計スコアを更新"):
            # 現在のスコアリストから差分を計算し、最後のスコアに加算する
            if scores[selected_player]:
                last_score_adjustment = new_total_score - current_total_score
                scores[selected_player][-1] += last_score_adjustment
            else:
                # まだスコアがない場合は新しいスコアをリストに追加
                scores[selected_player] = [new_total_score]

            save_data(scores, FILE_PATH)
            st.sidebar.success("合計スコアが更新されました。")
            st.experimental_rerun()

    # 承認待ちのスコアの処理（既存の機能）
    pending_scores = load_data(PENDING_PATH)
    to_remove = []
    for player, score_details in list(pending_scores.items()):
        input_score, adjusted_score, is_approved = score_details
        if not is_approved:
            col1, col2 = st.sidebar.columns(2)
            if col1.button(f"{player}: {input_score}点を承認", key=f"approve_{player}"):
                pending_scores[player] = [input_score, adjusted_score, True]
                if player not in scores:
                    scores[player] = []
                scores[player].append(adjusted_score)
                save_data(pending_scores, PENDING_PATH)
                save_data(scores, FILE_PATH)
                st.sidebar.success(f"{player}の点数を追加しました")
                st.experimental_rerun()
            if col2.button(f"{player}の申請却下", key=f"reject_{player}"):
                to_remove.append(player)
    for player in to_remove:
        del pending_scores[player]
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
        total_input_score = 0  # 入力されたスコアの合計値を初期化

        for player in selected_players:
            input_score = st.session_state[player]
            total_input_score += input_score  # 各プレイヤーのスコアを合計に加算

        # 入力された合計値が10,500点または100,000点であるかの確認
        if total_input_score == 105000 or total_input_score == 100000:
            for player in selected_players:
                input_score = st.session_state[player]
                adjusted_score = input_score - initial_points
                
                # input_score を追加して保存
                pending_scores[player] = [input_score, adjusted_score, False]
                save_data(pending_scores, PENDING_PATH)
                st.success(f"{player}の{input_score}点の申請を受け付けました。{adjusted_score//1000}点を追加します。")
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
