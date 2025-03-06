import streamlit as st # type: ignor
import pandas as pd
import plotly.express as px # type: ignore
from datetime import datetime, timedelta
import time
from scraper import scrape_product
from utils import (
    validate_url, load_products, save_products,
    load_price_history, save_price_history, format_price
)

st.set_page_config(
    page_title="Monitor de Preços",
    page_icon="📊",
    layout="wide"
)

# Styling
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .product-card {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("📊 Monitor de Preços")
    
    # Initialize session state
    if 'products_df' not in st.session_state:
        st.session_state.products_df = load_products()
    
    # Add new product section
    st.subheader("Adicionar Novo Produto")
    with st.form("add_product"):
        url = st.text_input("URL do Produto")
        submitted = st.form_submit_button("Adicionar Produto")
        
        if submitted and url:
            is_valid, error_msg = validate_url(url)
            if is_valid:
                try:
                    with st.spinner("Buscando informações do produto..."):
                        product_data = scrape_product(url)
                        
                    if product_data:
                        # Add to products DataFrame
                        new_row = pd.DataFrame({
                            'url': [url],
                            'product_name': [product_data['product_name']],
                            'last_price': [product_data['price']],
                            'last_check': [product_data['date']]
                        })
                        
                        st.session_state.products_df = pd.concat([st.session_state.products_df, new_row], ignore_index=True)
                        save_products(st.session_state.products_df)
                        save_price_history(url, product_data)
                        st.success("Produto adicionado com sucesso!")
                    else:
                        st.error("Não foi possível encontrar o preço do produto.")
                except Exception as e:
                    st.error(f"Erro ao adicionar produto: {str(e)}")
            else:
                st.error(error_msg)
    
    # Display products
    if not st.session_state.products_df.empty:
        st.subheader("Produtos Monitorados")
        
        cols = st.columns(2)
        for idx, row in st.session_state.products_df.iterrows():
            with cols[idx % 2]:
                with st.container():
                    st.markdown("---")
                    st.markdown(f"### {row['product_name']}")
                    st.markdown(f"**Último Preço:** {format_price(row['last_price'])}")
                    st.markdown(f"**Última Verificação:** {row['last_check']}")
                    
                    # Price history chart
                    history_df = load_price_history(row['url'])
                    if not history_df.empty:
                        fig = px.line(
                            history_df,
                            x='date',
                            y='price',
                            title="Histórico de Preços"
                        )
                        fig.update_layout(
                            yaxis_title="Preço (R$)",
                            xaxis_title="Data"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Update and remove buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Atualizar Preço##{idx}"):
                            try:
                                with st.spinner("Atualizando preço..."):
                                    product_data = scrape_product(row['url'])
                                if product_data:
                                    st.session_state.products_df.loc[idx, 'last_price'] = product_data['price']
                                    st.session_state.products_df.loc[idx, 'last_check'] = product_data['date']
                                    save_products(st.session_state.products_df)
                                    save_price_history(row['url'], product_data)
                                    st.success("Preço atualizado!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar preço: {str(e)}")
                    
                    with col2:
                        if st.button(f"Remover Produto##{idx}"):
                            st.session_state.products_df = st.session_state.products_df.drop(idx)
                            save_products(st.session_state.products_df)
                            st.success("Produto removido!")
                            st.rerun()
    else:
        st.info("Nenhum produto monitorado ainda. Adicione um produto para começar!")

if __name__ == "__main__":
    main()
