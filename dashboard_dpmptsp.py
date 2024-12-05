import pandas as pd
import streamlit as st
import plotly.graph_objects as go



# Set page config
st.set_page_config(page_title = "DPMPTSP Dashboard", layout="wide")


# Header
t1, t2 = st.columns((0.07,1))

t1.image('dpmptsp_logo2.jpeg', width = 100)
t2.title('Dashboard Tipologi DPMPTSP Jakarta')
t2.markdown("**tel :** 1500164 / (021)1500164 **| website :** https://pelayanan.jakarta.go.id/ **")

with st.spinner('Updating Report .... ') : 

    # Metrics setting and rendering

    ct_izin_df = pd.read_excel('ct_izin.xlsx',sheet_name = 'service_point')
    sp = st.selectbox('Choose Service Point', ct_izin_df, help = 'Filter report to show only one service point of penanaman modal')

    # label logic : determine if kecamatan, kelurahan or kota
    if sp.startswith('Kantor Camat') : 
        level = 'kecamatan' 
    elif sp.startswith('Kantor Lurah') : 
        level = 'kelurahan'
    else :
        level = 'kota / kabupaten'

 # Add tabs
    tab1, tab2 = st.tabs(["Izin Usaha", "Investasi & Pengawasan"])

    with tab1:
        # Data total izin berdasarkan status
        tot_status_df = pd.read_excel('ct_izin.xlsx', sheet_name='tot_status')
        filtered_data = tot_status_df[tot_status_df['service_point'] == sp]

        if not filtered_data.empty:
            total_izin = filtered_data['total_diajukan'].iloc[0]
            average_izin = filtered_data['average_status'].iloc[0]
            selesai_diproses = filtered_data['total_selesai'].iloc[0]
            ditolak_dibatalkan = filtered_data['total_ditolak_dibatalkan'].iloc[0]
            masih_diproses = filtered_data['total_proses'].iloc[0]

            # percentage
            selesai_perc = (selesai_diproses / total_izin) * 100
            ditolak_perc = (ditolak_dibatalkan / total_izin) * 100
            masih_perc = (masih_diproses / total_izin) * 100

            # Define layout using column in streamlit
            m1, m2, m3 = st.columns((1, 1, 1))
            m1.metric(label="Total Izin yang diajukan", value=total_izin)
            m2.metric(label="Selesai diproses", value=selesai_diproses, delta=f"{round(selesai_perc, 1)}%")
            m3.metric(label="Masih diproses", value=masih_diproses, delta=f"{round(masih_perc, 1)}%")

            c1, c2 = st.columns((1, 1))
            c1.metric(label="Ditolak & dibatalkan", value=ditolak_dibatalkan, delta=f"{round(ditolak_perc, 1)}%")
            c2.metric(label="Rata-rata izin per " + level.capitalize(), value=f"{average_izin:.1f}")

            st.markdown("---")

            # Layout untuk grafik pie chart dan klasifikasi cluster
            g1, g2 = st.columns((1, 1))

            pcdf = pd.read_excel('ct_izin.xlsx', sheet_name='tot_bidang2')
            pcdf = pcdf[pcdf['service_point'] == sp]

            fig1 = go.Figure(data=[go.Pie(labels=pcdf['bidang_recode'], values=pcdf['total_diajukan'], hole=.3, marker=dict(colors=['#264653']))])
            fig1.update_layout(title_text="Kategori Bidang yang Dominan", title_x=0, margin=dict(l=0, r=10, b=10))

            cidf = pd.read_excel('ct_izin.xlsx', sheet_name='cluster')
            cidf = cidf[cidf['service_point'] == sp]

            if not cidf.empty:
                cluster_value = cidf['Cluster'].iloc[0]

                if cluster_value == 0:
                    lvl_cluster = 'didominasi di Bidang **Pelayanan umum dan penataan ruang**, Bidang **Kesehatan** dan Bidang **Pelayanan Administrasi**'
                elif cluster_value == 1:
                    lvl_cluster = 'didominasi hanya di Bidang **Pelayanan Administrasi**'
                elif cluster_value == 3:
                    lvl_cluster = 'didominasi utama di Bidang **Kesehatan**'
                elif cluster_value == 4:
                    lvl_cluster = 'menonjol pada bidang kesehatan yang lebih mendominasi dibandingkan cluster3'
                elif cluster_value == 6:
                    lvl_cluster = 'didominasi utama di Bidang **Pelayanan Administrasi** dan bidang Kesbangpol'
                elif cluster_value == 7:
                    lvl_cluster = 'cukup menyebar rata seperti Kesbangpol, Kesehatan, Lingkungan Hidup'
                else:
                    lvl_cluster = 'tidak ditemukan cluster ini'

                g1.markdown(f"## <h2 style='color: blue;'> Cluster {cluster_value}</h2>", unsafe_allow_html=True)
                g1.markdown(f"### Cluster ini {lvl_cluster}")
                g2.plotly_chart(fig1, use_container_width=True)
            
            st.markdown("---")

             # Bar chart: Tipe Pemohon
            g3 = st.columns(1)[0]
            pdf = pd.read_excel('ct_izin.xlsx', sheet_name='pemohon')
            pdf = pdf[pdf['service_point'] == sp]

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                y=pdf['service_point'],
                x=pdf['perorangan'],
                name='Perorangan',
                orientation='h',
                text=pdf['perorangan'],
                textposition='auto'
            ))
            fig2.add_trace(go.Bar(
                y=pdf['service_point'],
                x=pdf['perusahaan'],
                name='Perusahaan',
                orientation='h',
                text=pdf['perusahaan'],
                textposition='auto'
            ))

            fig2.update_layout(
                barmode='stack',
                title={
                    'text': 'Tipe Pemohon berdasarkan Jumlah izin: Perorangan vs Perusahaan',
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                height=300,
                xaxis={
                    'showticklabels': False
                }
            )

            g3.plotly_chart(fig2, use_container_width=True)

            st.markdown("## Distribusi Bidang Perizinan")

            # Baca data wilayah
            wdf = pd.read_excel('ct_izin.xlsx', sheet_name='wilayah_derivative')
            selected_row = wdf[wdf['service_point'] == sp].iloc[0]
            level_wilayah = selected_row['Level_wilayah']

            # Color palette
            colors = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
                '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'
            ]

            # Daftar kolom bidang
            bidang_cols = ['Esdm', 'Kehutanan', 'Kelautan Dan Perikanan', 'Kepemudaan dan Keolahragaan',
                        'Kesatuan Bangsa Dan Politik Dalam Negeri', 'Kesehatan', 
                        'Ketenteraman, ketertiban Umum dan Pelindungan Masyarakat',
                        'Lingkungan Hidup', 'Pariwisata', 'Pekerjaan Umum Dan Penataan Ruang',
                        'Pelayanan Administrasi', 'Pendidikan', 'Perdagangan', 'Perhubungan',
                        'Pertanahan Yang Menjadi Kewenangan Daerah', 'Pertanian',
                        'Perumahan Rakyat Dan Kawasan Permukiman', 'Sosial', 'Tenaga Kerja']

            if level_wilayah == 'Kel':
                st.info("Data sama dengan Pie Chart diatas")

            elif level_wilayah == 'Dinas':
                # Data untuk level dinas
                dinas = selected_row['dinas']
                dinas_data = wdf[wdf['dinas'] == dinas]
        
                # Agregasi data per kota
                agg_data = dinas_data.groupby('kota')[bidang_cols].sum().reset_index()
                agg_data['total'] = agg_data[bidang_cols].sum(axis=1)
        
                fig = go.Figure()
                color_idx = 0
                for bidang in bidang_cols:
                    if agg_data[bidang].sum() > 0:
                        fig.add_trace(go.Bar(
                            y=agg_data['kota'],
                            x=agg_data[bidang] / agg_data['total'] * 100,
                            name=bidang,
                            orientation='h',
                            text=[f'{x:.1f}% ({int(y)})' for x, y in zip(agg_data[bidang] / agg_data['total'] * 100, agg_data[bidang])],
                            textposition='inside',
                            marker_color=colors[color_idx % len(colors)],
                            legendgroup=bidang,
                            showlegend=True
                        ))
                        color_idx += 1
                title_text = f'Distribusi Bidang Perizinan untuk Dinas {dinas}'

            elif level_wilayah == 'Kota':
                # Data untuk level kota
                kota = selected_row['kota']
                kota_data = wdf[wdf['kota'] == kota]
                agg_data = kota_data.groupby('kecamatan')[bidang_cols].sum().reset_index()
                agg_data['total'] = agg_data[bidang_cols].sum(axis=1)
        
                fig = go.Figure()
                color_idx = 0
                for bidang in bidang_cols:
                    if agg_data[bidang].sum() > 0:
                        fig.add_trace(go.Bar(
                            y=agg_data['kecamatan'],
                            x=agg_data[bidang] / agg_data['total'] * 100,
                            name=bidang,
                            orientation='h',
                            text=[f'{x:.1f}% ({int(y)})' for x, y in zip(agg_data[bidang] / agg_data['total'] * 100, agg_data[bidang])],
                            textposition='inside',
                            marker_color=colors[color_idx % len(colors)],
                            legendgroup=bidang,
                            showlegend=True
                        ))
                        color_idx += 1
                title_text = f'Distribusi Bidang Perizinan di Kota {kota}'

            elif level_wilayah == 'Kec':
                # Data untuk level kecamatan
                kecamatan = selected_row['kecamatan']
                kec_data = wdf[wdf['kecamatan'] == kecamatan]
                kec_data['total'] = kec_data[bidang_cols].sum(axis=1)
        
                fig = go.Figure()
                color_idx = 0
                for bidang in bidang_cols:
                    if kec_data[bidang].sum() > 0:
                        # Tangani nilai NaN dengan mengubah ke 0
                        values = kec_data[bidang].fillna(0)
                        percentages = (values / kec_data['total'] * 100).fillna(0)
                
                        fig.add_trace(go.Bar(
                            y=kec_data['service_point'],
                            x=percentages,
                            name=bidang,
                            orientation='h',
                            text=[f'{x:.1f}% ({int(y)})' if not pd.isna(y) else '0% (0)' 
                                for x, y in zip(percentages, values)],
                            textposition='inside',
                            marker_color=colors[color_idx % len(colors)],
                            legendgroup=bidang,
                            showlegend=True
                        ))
                        color_idx += 1
                title_text = f'Distribusi Bidang Perizinan di Kecamatan {kecamatan}'

            if level_wilayah != 'Kel':
                # Pengaturan layout grafik
                fig.update_layout(
                    barmode='stack',
                    title=title_text,
                    xaxis_title='Persentase (%)',
                    height=800,  # Tinggi grafik diperbesar
                    bargap=0.2,  # Jarak antar bar
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255, 255, 255, 0.8)',
                        bordercolor='rgba(0, 0, 0, 0.3)',
                        borderwidth=1,
                        itemsizing='constant',
                        itemwidth=40
                    ),
                    margin=dict(b=200),  # Margin bawah untuk legend
                    uniformtext=dict(mode='hide', minsize=8)
                )

                # Tambahkan button untuk toggle legend
                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            direction="left",
                            buttons=list([
                                dict(
                                    args=[{"visible": [True] * len(fig.data)}],
                                    label="Show All",
                                    method="restyle"
                                ),
                                dict(
                                    args=[{"visible": [False] * len(fig.data)}],
                                    label="Hide All",
                                    method="restyle"
                                )
                            ]),
                            pad={"r": 10, "t": 10},
                            showactive=True,
                            x=0.11,
                            xanchor="left",
                            y=1.1,
                            yanchor="top"
                        ),
                    ]
                )

                st.plotly_chart(fig, use_container_width=True)
            
            # Kalau g5 ini terkait berdasarkan distribusi berdasarkan sub wilayah

            with st.expander("## Distribusi Total Perizinan di Sub-wilayah", expanded=False):
                # Initialize sub_data as None
                sub_data = None

                if level_wilayah == 'Kota':
                    # For Kota level, show Kelurahan data
                    kecamatan = wdf[wdf['kota'] == selected_row['kota']]['kecamatan'].unique()
                    sub_data = wdf[wdf['kecamatan'].isin(kecamatan)].copy()
                    group_col = 'kelurahan'
                    title_text = f'Distribusi Total Perizinan per Kelurahan di {selected_row["kota"]}'
                elif level_wilayah == 'Dinas':
                    # For DPMPTSP DKI JAKARTA, show aggregated Kecamatan data
                    sub_data = wdf.copy()
                    group_col = 'kecamatan'
                    title_text = 'Distribusi Total Perizinan per Kecamatan di DKI Jakarta'

                if sub_data is not None:
                    # Calculate total for all bidang_cols
                    sub_data['total_izin'] = sub_data[bidang_cols].sum(axis=1)
            
                    # Aggregate data by sub-region
                    agg_sub_data = sub_data.groupby(group_col)['total_izin'].sum().reset_index()
            
                    # Sort by total
                    agg_sub_data = agg_sub_data.sort_values('total_izin', ascending=False)
            
                    # Rename columns for display
                    agg_sub_data.columns = ['Wilayah', 'Total Perizinan']
            
                    # Format the Total Perizinan column with thousands separator
                    agg_sub_data['Total Perizinan'] = agg_sub_data['Total Perizinan'].apply(lambda x: f"{int(x):,}")
            
                    # Display title
                    st.markdown(f"### {title_text}")
            
                    # Display table with styling
                    st.dataframe(
                        agg_sub_data,
                        height=400,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "Wilayah": st.column_config.TextColumn(
                                "Wilayah",
                                width="medium",
                            ),
                            "Total Perizinan": st.column_config.TextColumn(
                                "Total Perizinan",
                                width="medium",
                            )
                        },
                        column_order=["Wilayah", "Total Perizinan"]
                    )

            # Add new section for detailed permits
            with st.expander("## Detail Izin berdasarkan Bidang", expanded=False):
                try:
                    # Read the data
                    izin_detail_df = pd.read_excel('ct_izin.xlsx', sheet_name='nama_izin')
            
                    # Filter data based on selected service point
                    filtered_izin = izin_detail_df[izin_detail_df['service_point'] == sp].copy()
            
                    if not filtered_izin.empty:
                        # Ensure columns exist and handle missing data
                        required_columns = ['service_point', 'bidang_recode', 'nama_izin', 'total_selesai']
                        if all(col in filtered_izin.columns for col in required_columns):
                            # Group by bidang and nama_izin
                            grouped_izin = (filtered_izin
                                .groupby(['bidang_recode', 'nama_izin'])
                                .agg({'total_selesai': 'sum'})
                                .reset_index()
                                .sort_values('total_selesai', ascending=False)
                            )
                    
                            # Display the table
                            st.markdown(f"### Detail Izin di {sp}")
                            st.dataframe(
                                grouped_izin,
                                height=400,
                                hide_index=True,
                                use_container_width=True,
                                column_config={
                                    "bidang_recode": st.column_config.TextColumn(
                                        "Bidang",
                                        width="medium",
                                    ),
                                    "nama_izin": st.column_config.TextColumn(
                                        "Nama Izin",
                                        width="large",
                                    ),
                                    "total_selesai": st.column_config.NumberColumn(
                                        "Total Izin Selesai",
                                        width="small",
                                        format="%d"
                                    )
                                }
                            )
                    
                            # Display summary statistics
                            st.markdown("### Ringkasan")
                            col1, col2, col3 = st.columns(3)
                    
                            with col1:
                                st.metric("Total Jenis Izin", len(grouped_izin['nama_izin'].unique()))
                            with col2:
                                st.metric("Total Bidang", len(grouped_izin['bidang_recode'].unique()))
                            with col3:
                                st.metric("Total Izin Selesai", int(grouped_izin['total_selesai'].sum()))
                        else:
                            st.error("Format data tidak sesuai. Mohon periksa kolom yang diperlukan.")
                    else:
                        st.info("Tidak ada data izin untuk service point ini")
                
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")   

        # ------------------------------------------------------------------------------------------------------------------
        ## Tab 2 Bagian Investasi             
        # ------------------------------------------------------------------------------------------------------------------

    with tab2:
        # Data jumlah investasi, dan pengawasan
        tot_investasi_df = pd.read_excel('ct_investasi_dimas.xlsx', sheet_name='All')
        filtered_data_inv = tot_investasi_df[tot_investasi_df['service_point'] == sp]

        # Data cluster investasi
        cluster_investasi_df = pd.read_excel('ct_investasi_dimas.xlsx', sheet_name='Cluster')
        filtered_data_invc = cluster_investasi_df[cluster_investasi_df['service_point'] == sp]

        if not filtered_data_inv.empty : 
            total_investasi = filtered_data_inv['Jumlah_Investasi'].iloc[0]
            pengawasan_r = filtered_data_inv['Rendah'].iloc[0]
            pengawasan_mr = filtered_data_inv['Menengah Rendah'].iloc[0]
            pengawasan_mt = filtered_data_inv['Menengah Tinggi'].iloc[0]
            pengawasan_t = filtered_data_inv['Tinggi'].iloc[0]
            total_pengawasan = pengawasan_r + pengawasan_mr + pengawasan_mt + pengawasan_t

            pengawasan_r_perc = (pengawasan_r / total_pengawasan) * 100
            pengawasan_mr_perc = (pengawasan_mr / total_pengawasan) * 100
            pengawasan_mt_perc = (pengawasan_mt / total_pengawasan) * 100
            pengawasan_t_perc = (pengawasan_t / total_pengawasan) * 100

            # Define column untuk pengawasan dan investasi
            st.subheader(f"Monitoring Metrics for {sp}")
            inv1, inv2, inv3 = st.columns((1, 1, 1))
            inv1.write('')
            inv2.metric(label = "Total Investasi", value = f"Rp {total_investasi:,.0f}")
            inv2.caption(f'_dengan rata-rata investasi sekitar **Rp {total_investasi/1000000000:,.0f} bio**_')
            inv3.write('')

            st.divider()
            
            peng1, peng2, peng3, peng4 = st.columns((1, 1, 1, 1))
            peng1.metric(label = "Pengawasan Resiko Rendah", value = f"{pengawasan_r:,}", delta =f"{round(pengawasan_r_perc, 1)}%")
            peng2.metric(label = "Pengawasan Resiko Menengah Rendah", value = f"{pengawasan_mr:,}", delta =f"{round(pengawasan_mr_perc, 1)}%")
            peng3.metric(label = "Pengawasan Resiko Menengah Tinggi", value = f"{pengawasan_mt:,}", delta =f"{round(pengawasan_mt_perc, 1)}%")
            peng4.metric(label = "Pengawasan Resiko Tinggi", value = f"{pengawasan_t:,}", delta =f"{round(pengawasan_t_perc, 1)}%")
        
            st.markdown("---")

            # Jumlah Usaha yang ada di daerah tsb
            # Persiapan variabelnya dulu
            values_ju = [
                filtered_data_inv['Usaha Besar'].sum()
                , filtered_data_inv['Usaha Menengah'].sum()
                , filtered_data_inv['Usaha Kecil'].sum()
                , filtered_data_inv['Usaha Mikro'].sum()
            ]
            labels_ju = ['Usaha Besar', 'Usaha Menengah', 'Usaha Kecil', 'Usaha Mikro']

            values_jp = [
                filtered_data_inv['Badan Hukum Lainnya'].sum()
                , filtered_data_inv['Badan Layanan Umum (BLU)'].sum()
                , filtered_data_inv['Koperasi'].sum()
                , filtered_data_inv['Lembaga dan Bentuk Lainnya'].sum()
                , filtered_data_inv['Organisasi Lainnya'].sum()
                , filtered_data_inv['Perorangan'].sum()
                , filtered_data_inv['Persekutuan Firma (Fa / Venootschap Onder Firma)'].sum()
                , filtered_data_inv['Persekutuan Perdata'].sum()
                , filtered_data_inv['Perseroan Lainnya'].sum()
                , filtered_data_inv['Perseroan Terbatas (PT)'].sum()
                , filtered_data_inv['Perseroan Terbatas (PT) Perorangan'].sum()
                , filtered_data_inv['Perusahaan Umum (Perum)'].sum()
                , filtered_data_inv['Perusahaan Umum Daerah (Perumda)'].sum()
                , filtered_data_inv['Yayasan'].sum()
            ]
            labels_jp = [
                'Badan Hukum Lainnya'
                , 'Badan Layanan Umum (BLU)'
                , 'Koperasi'
                , 'Lembaga dan Bentuk Lainnya'
                , 'Organisasi Lainnya'
                , 'Perorangan'
                , 'Persekutuan Firma (Fa / Venootschap Onder Firma)'
                , 'Persekutuan Perdata'
                , 'Perseroan Lainnya'
                , 'Perseroan Terbatas (PT)'
                , 'Perseroan Terbatas (PT) Perorangan'
                , 'Perusahaan Umum (Perum)'
                , 'Perusahaan Umum Daerah (Perumda)'
                , 'Yayasan'
            ]

            
            # Pembuatan plotlynya terkait jumlah usaha dan jenis perusahaan
            fig_ju = go.Figure(data=[go.Pie(labels=labels_ju, values=values_ju, hole=.3, marker=dict(colors=['#264653']))])
            fig_jp = go.Figure(data=[go.Pie(labels=labels_jp, values=values_jp, hole=.3, marker=dict(colors=['#264653']))])

            fig_ju.update_layout(title = "Pie Chart berdasarkan Jumlah Usaha", title_x = 0.5)
            fig_jp.update_layout(title = "Pie Chart berdasarkan Jenis Perusahaan", title_x = 0.5)

            st.subheader(f"Jumlah Usaha dan Jenis Perusahaan {sp}")

            # Pembuatan element di streamlitnya 
            ju1, ju2 = st.columns((1,1))
            ju1.plotly_chart(fig_ju, use_container_width = True)
            ju2.plotly_chart(fig_jp, use_container_width = True)

            st.markdown("---")
        
        else : 
            st.warning(f"No data available for this service point yet")