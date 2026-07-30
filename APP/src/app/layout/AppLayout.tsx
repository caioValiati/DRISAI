import { useMemo } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Avatar, Dropdown, Layout, Menu, Typography } from 'antd'
import {
  ExperimentOutlined,
  GoldOutlined,
  HomeOutlined,
  LogoutOutlined,
  MedicineBoxOutlined,
  PartitionOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { useAuth } from '@/app/providers/AuthContext'

const { Header, Sider, Content } = Layout

export function AppLayout() {
  const { usuario, sair } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  // RF003 — o menu reflete o perfil: Admin cuida da curadoria; Agrônomo, da consultoria
  const itens = useMemo(() => {
    if (usuario?.perfil === 'ADMIN') {
      return [
        { key: '/normas', icon: <ExperimentOutlined />, label: <Link to="/normas">Normas DRIS</Link> },
        { key: '/insumos', icon: <MedicineBoxOutlined />, label: <Link to="/insumos">Insumos</Link> },
      ]
    }
    return [
      { key: '/produtores', icon: <TeamOutlined />, label: <Link to="/produtores">Produtores</Link> },
      { key: '/propriedades', icon: <HomeOutlined />, label: <Link to="/propriedades">Propriedades</Link> },
      { key: '/talhoes', icon: <PartitionOutlined />, label: <Link to="/talhoes">Talhões</Link> },
      { key: '/amostras', icon: <GoldOutlined />, label: <Link to="/amostras">Amostras foliares</Link> },
    ]
  }, [usuario?.perfil])

  const selecionado = itens.find((item) => location.pathname.startsWith(item.key))?.key

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0" theme="light" width={230}>
        <div style={{ padding: '20px 16px' }}>
          <Typography.Title level={4} style={{ margin: 0, color: '#2e7d32' }}>
            DRISAI
          </Typography.Title>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            Gestão nutricional agrícola
          </Typography.Text>
        </div>
        <Menu mode="inline" selectedKeys={selecionado ? [selecionado] : []} items={itens} />
      </Sider>

      <Layout>
        <Header
          style={{
            background: '#fff',
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            paddingInline: 24,
          }}
        >
          <Dropdown
            menu={{
              items: [
                { key: 'perfil', icon: <UserOutlined />, label: 'Meu perfil' },
                { type: 'divider' },
                { key: 'sair', icon: <LogoutOutlined />, label: 'Sair', danger: true },
              ],
              onClick: async ({ key }) => {
                if (key === 'perfil') navigate('/perfil')
                if (key === 'sair') {
                  await sair()
                  navigate('/login')
                }
              },
            }}
          >
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar style={{ background: '#2e7d32' }} icon={<UserOutlined />} />
              <div style={{ lineHeight: 1.2 }}>
                <div style={{ fontWeight: 500 }}>{usuario?.nome}</div>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {usuario?.perfil === 'ADMIN' ? 'Administrador' : 'Agrônomo'}
                </Typography.Text>
              </div>
            </div>
          </Dropdown>
        </Header>

        <Content style={{ padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
