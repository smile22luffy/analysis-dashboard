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
    
    # CSV取り込み機能
    st.subheader("📂 データの選択")
    data_source = st.radio(
        "データソースを選択",
        ["サンプルデータを使用", "CSVファイルをアップロード"]
    )
    
    if data_source == "CSVファイルをアップロード":
        uploaded_file = st.file_uploader(
            "売上データのCSVファイルをアップロード", 
            type="csv",
            help="列名例: 日付, 売上, 商品カテゴリ, 地域"
        )
        
        if uploaded_file is not None:
            try:
                # CSVを読み込み
                sales_data = pd.read_csv(uploaded_file)
                
                # データの形式確認
                st.success(f"✅ データを読み込みました！({len(sales_data)}行)")
                
                # 列名の表示
                st.write("**列名:**", list(sales_data.columns))
                
                # データプレビュー
                with st.expander("データプレビュー"):
                    st.dataframe(sales_data.head())
                
                # 列名のマッピング
                st.subheader("📋 列名の設定")
                col1, col2 = st.columns(2)
                
                with col1:
                    date_col = st.selectbox("日付列", sales_data.columns)
                    amount_col = st.selectbox("売上金額列", sales_data.columns)
                
                with col2:
                    category_col = st.selectbox("カテゴリ列", sales_data.columns, index=min(2, len(sales_data.columns)-1))
                    region_col = st.selectbox("地域列", sales_data.columns, index=min(3, len(sales_data.columns)-1))
                
                # データ変換と分析
                if st.button("📊 分析開始"):
                    try:
                        # 日付変換
                        sales_data[date_col] = pd.to_datetime(sales_data[date_col])
                        sales_data[amount_col] = pd.to_numeric(sales_data[amount_col], errors='coerce')
                        
                        # 分析実行
                        analyze_sales_data(sales_data, date_col, amount_col, category_col, region_col)
                        
                    except Exception as e:
                        st.error(f"データ処理エラー: {str(e)}")
                        st.info("日付形式や数値形式を確認してください")
                        
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {str(e)}")
                st.info("CSVファイルの形式を確認してください")
        else:
            st.info("👆 CSVファイルをアップロードしてください")
    
    else:
        # サンプルデータを使用（既存のコード）
        st.info("サンプルデータを使用しています")
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=365)
        sales_data = pd.DataFrame({
            '日付': dates,
            '売上': np.random.normal(100000, 20000, 365),
            '商品カテゴリ': np.random.choice(['A', 'B', 'C'], 365),
            '地域': np.random.choice(['東京', '大阪', '名古屋'], 365)
        })
        analyze_sales_data(sales_data, '日付', '売上', '商品カテゴリ', '地域')

def analyze_sales_data(sales_data, date_col, amount_col, category_col, region_col):
    """売上データの分析を実行"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("月別売上推移")
        try:
            monthly_sales = sales_data.groupby(sales_data[date_col].dt.month)[amount_col].sum()
            st.line_chart(monthly_sales)
        except Exception as e:
            st.error(f"月別売上グラフエラー: {str(e)}")
    
    with col2:
        st.subheader("カテゴリ別売上")
        try:
            category_sales = sales_data.groupby(category_col)[amount_col].sum()
            st.bar_chart(category_sales)
        except Exception as e:
            st.error(f"カテゴリ別売上グラフエラー: {str(e)}")
    
    # 統計情報
    st.subheader("📊 統計情報")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総売上", f"¥{sales_data[amount_col].sum():,.0f}")
    with col2:
        st.metric("平均売上", f"¥{sales_data[amount_col].mean():,.0f}")
    with col3:
        st.metric("データ件数", f"{len(sales_data):,}件")
    with col4:
        try:
            st.metric("期間", f"{sales_data[date_col].dt.date.min()} - {sales_data[date_col].dt.date.max()}")
        except:
            st.metric("期間", "N/A")
    
    # 詳細データテーブル
    st.subheader("📋 詳細データ")
    st.dataframe(sales_data.head(10))
    
    # ダウンロード機能
    csv = sales_data.to_csv(index=False)
    st.download_button(
        label="📥 分析結果をCSVダウンロード",
        data=csv,
        file_name="sales_analysis_result.csv",
        mime="text/csv"
    )
    
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

def analyze_sales_data(sales_data, date_col, amount_col, category_col, region_col):
    """売上データの分析を実行"""    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("月別売上推移")
        try:
            monthly_sales = sales_data.groupby(sales_data[date_col].dt.month)[amount_col].sum()
            st.line_chart(monthly_sales)
        except Exception as e:
            st.error(f"月別売上グラフエラー: {str(e)}")
    
    with col2:
        st.subheader("カテゴリ別売上")
        try:
            category_sales = sales_data.groupby(category_col)[amount_col].sum()
            st.bar_chart(category_sales)
        except Exception as e:
            st.error(f"カテゴリ別売上グラフエラー: {str(e)}")
    
    # 統計情報
    st.subheader("📊 統計情報")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総売上", f"¥{sales_data[amount_col].sum():,.0f}")
    with col2:
        st.metric("平均売上", f"¥{sales_data[amount_col].mean():,.0f}")
    with col3:
        st.metric("データ件数", f"{len(sales_data):,}件")
    with col4:
        try:
            st.metric("期間", f"{sales_data[date_col].dt.date.min()} - {sales_data[date_col].dt.date.max()}")
        except:
            st.metric("期間", "N/A")
    
    # 詳細データテーブル
    st.subheader("📋 詳細データ")
    st.dataframe(sales_data.head(10))
    
    # ダウンロード機能
    csv = sales_data.to_csv(index=False)
    st.download_button(
        label="📥 分析結果をCSVダウンロード",
        data=csv,
        file_name="sales_analysis_result.csv",
        mime="text/csv"
    )

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
