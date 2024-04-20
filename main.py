import streamlit as st

# タイトル
st.title('麻雀点数記録アプリ')

# 初期化
if 'scores' not in st.session_state:
    st.session_state['scores'] = {}
if 'input_scores' not in st.session_state:
    st.session_state['input_scores'] = {}

# プレイヤー名のリスト
player_names = [f'プレイヤー{i+1}' for i in range(20)]

# プレイヤーの選択
selected_players = st.multiselect('プレイヤーを選択してください（3人または4人）', player_names)

# 点数入力用の辞書を初期化
for player in selected_players:
    if player not in st.session_state['input_scores']:
        st.session_state['input_scores'][player] = 0

# 点数入力セクション
for player in selected_players:
    st.session_state['input_scores'][player] = st.number_input(f'{player}の点数', key=f'score_{player}', value=st.session_state['input_scores'][player])

# 点数を一斉に追加
if st.button('点数を全員に追加'):
    for player, score in st.session_state['input_scores'].items():
        if score != 0:
            if player not in st.session_state['scores']:
                st.session_state['scores'][player] = []
            st.session_state['scores'][player].append(score)
            st.success(f'{player}に{score}点を追加しました')
            # 入力をリセット
            st.session_state['input_scores'][player] = 0

# 順位の計算と表示
if st.button('順位を表示'):
    # 合計点数の計算
    total_scores = {player: sum(scores) for player, scores in st.session_state['scores'].items() if player in selected_players}
    # 順位のソート
    sorted_scores = dict(sorted(total_scores.items(), key=lambda item: item[1], reverse=True))
    st.subheader('順位')
    for idx, (player, score) in enumerate(sorted_scores.items(), 1):
        st.write(f"{idx}位: {player} - {score}点")

# ログの表示
with st.expander("点数ログ"):
    for player, scores in st.session_state['scores'].items():
        if player in selected_players:
            st.write(f"{player}: 各ゲームの点数 {scores} / 合計点数 {sum(scores)}点")
