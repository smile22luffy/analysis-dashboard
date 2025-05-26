import streamlit as st
import hashlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ページ設定
st.set_page_config(
    page_title="分析ダッシュボード",
    page_icon="📊",
    layout="wide"
)

def authenticate():
    """基本認証システム"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 分析ダッシュボード - ログイン")
        
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("---")
            username = st.text_input("ユーザー名")
            password = st.text_input("パスワード", type="password")
            
            if st.button("ログイン", use_container_width=True):
                # ユーザー情報
                users = {
                    "admin": st.secrets["ADMIN_PASS_HASH"],
                    "analyst": st.secrets["ANALYST_PASS_HASH"]
                }
                
                hashed = hashlib.sha256(password.encode()).hexdigest()
                if username in users and users[username] == hashed:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("ログイン成功！")
                    st.rerun()
                else:
                    st.error("認証に失敗しました")
                    
            st.markdown("---")
            st.caption("テスト用: admin/password または analyst/hello123")
        return False
    return True

def logout():
    """ログアウト処理"""
    if st.sidebar.button("🚪 ログアウト"):
        st.session_state.authenticated = False
        st.rerun()

def sales_analysis():
    """売上分析ツール"""
    st.header("📈 売上分析")
    
    # サンプルデータ生成
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=365)
    sales_data = pd.DataFrame({
        '日付': dates,
        '売上': np.random.normal(100000, 20000, 365),
        '商品カテゴリ': np.random.choice(['A', 'B', 'C'], 365),
        '地域': np.random.choice(['東京', '大阪', '名古屋'], 365)
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("月別売上推移")
        monthly_sales = sales_data.groupby(sales_data['日付'].dt.month)['売上'].sum()
        st.line_chart(monthly_sales)
    
    with col2:
        st.subheader("カテゴリ別売上")
        category_sales = sales_data.groupby('商品カテゴリ')['売上'].sum()
        st.bar_chart(category_sales)
    
    st.subheader("詳細データ")
    st.dataframe(sales_data.head(10))

def customer_analysis():
    """顧客分析ツール"""
    st.header("👥 顧客分析")
    
    # サンプルデータ
    np.random.seed(123)
    customer_data = pd.DataFrame({
        '顧客ID': range(1, 1001),
        '年齢': np.random.randint(20, 70, 1000),
        '購入回数': np.random.poisson(5, 1000),
        '総購入額': np.random.gamma(2, 50000, 1000),
        '性別': np.random.choice(['男性', '女性'], 1000)
    })
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("総顧客数", f"{len(customer_data):,}人")
    
    with col2:
        st.metric("平均購入額", f"¥{customer_data['総購入額'].mean():,.0f}")
    
    with col3:
        st.metric("平均購入回数", f"{customer_data['購入回数'].mean():.1f}回")
    
    # フィルター
    age_range = st.slider("年齢範囲", 20, 70, (25, 65))
    
    filtered_data = customer_data[
        (customer_data['年齢'] >= age_range[0]) & 
        (customer_data['年齢'] <= age_range[1])
    ]
    
    st.subheader("年齢分布")
    fig, ax = plt.subplots()
    ax.hist(filtered_data['年齢'], bins=20, alpha=0.7)
    ax.set_xlabel('年齢')
    ax.set_ylabel('人数')
    st.pyplot(fig)

def inventory_analysis():
    """在庫分析ツール"""
    st.header("📦 在庫分析")
    
    # サンプルデータ
    np.random.seed(456)
    inventory_data = pd.DataFrame({
        '商品名': [f'商品{i:03d}' for i in range(1, 101)],
        '在庫数': np.random.randint(0, 500, 100),
        '単価': np.random.randint(100, 10000, 100),
        'カテゴリ': np.random.choice(['電子機器', '衣類', '食品', '書籍'], 100),
    })
    
    inventory_data['在庫金額'] = inventory_data['在庫数'] * inventory_data['単価']
    
    # 在庫アラート
    low_stock = inventory_data[inventory_data['在庫数'] < 50]
    if len(low_stock) > 0:
        st.warning(f"⚠️ 在庫不足商品が{len(low_stock)}件あります")
        st.dataframe(low_stock[['商品名', '在庫数', 'カテゴリ']])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("カテゴリ別在庫金額")
        category_value = inventory_data.groupby('カテゴリ')['在庫金額'].sum()
        st.bar_chart(category_value)
    
    with col2:
        st.subheader("在庫数トップ10")
        top_stock = inventory_data.nlargest(10, '在庫数')[['商品名', '在庫数']]
        st.dataframe(top_stock)

def main():
    """メインアプリケーション"""
    if not authenticate():
        return
    
    # サイドバー
    st.sidebar.title("📊 分析ダッシュボード")
    st.sidebar.markdown(f"ようこそ、**{st.session_state.username}**さん！")
    
    # ツール選択
    tool = st.sidebar.selectbox(
        "分析ツールを選択",
        ["売上分析", "顧客分析", "在庫分析"]
    )
    
    # ログアウトボタン
    logout()
    
    # メインコンテンツ
    if tool == "売上分析":
        sales_analysis()
    elif tool == "顧客分析":
        customer_analysis()
    elif tool == "在庫分析":
        inventory_analysis()

if __name__ == "__main__":
    main()
