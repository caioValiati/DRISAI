import { useMemo } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { Avatar, Dropdown, Flex, Layout, Menu, Typography } from "antd";
import {
  ExperimentOutlined,
  GoldOutlined,
  HomeOutlined,
  LogoutOutlined,
  MedicineBoxOutlined,
  PartitionOutlined,
  TeamOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { useAuth } from "@/app/providers/AuthContext";

const { Header, Sider, Content } = Layout;

export function AppLayout() {
  const { usuario, sair } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const itens = useMemo(() => {
    if (usuario?.perfil === "ADMIN") {
      return [
        {
          key: "/normas",
          icon: <ExperimentOutlined />,
          label: <Link to="/normas">Normas DRIS</Link>,
        },
        {
          key: "/insumos",
          icon: <MedicineBoxOutlined />,
          label: <Link to="/insumos">Insumos</Link>,
        },
        {
          key: "/produtores",
          icon: <TeamOutlined />,
          label: <Link to="/produtores">Produtores</Link>,
        },
        {
          key: "/propriedades",
          icon: <HomeOutlined />,
          label: <Link to="/propriedades">Propriedades</Link>,
        },
        {
          key: "/talhoes",
          icon: <PartitionOutlined />,
          label: <Link to="/talhoes">Talhões</Link>,
        },
        {
          key: "/amostras",
          icon: <GoldOutlined />,
          label: <Link to="/amostras">Amostras foliares</Link>,
        },
      ];
    }
    return [
      {
        key: "/produtores",
        icon: <TeamOutlined />,
        label: <Link to="/produtores">Produtores</Link>,
      },
      {
        key: "/propriedades",
        icon: <HomeOutlined />,
        label: <Link to="/propriedades">Propriedades</Link>,
      },
      {
        key: "/talhoes",
        icon: <PartitionOutlined />,
        label: <Link to="/talhoes">Talhões</Link>,
      },
      {
        key: "/amostras",
        icon: <GoldOutlined />,
        label: <Link to="/amostras">Amostras foliares</Link>,
      },
    ];
  }, [usuario?.perfil]);

  const selecionado = itens.find((item) =>
    location.pathname.startsWith(item.key),
  )?.key;

  return (
    <Layout style={{ height: "100vh", overflow: "hidden" }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        theme="dark"
        width={230}
        style={{
          height: "100vh",
          overflow: "auto",
          borderRight: "1px solid #f0f0f0",
        }}
      >
        <div style={{ padding: "16px", borderRadius: "8px", maxWidth: "300px" }}>
          <Flex gap={12} align="center">
            <Avatar
              shape="square"
              size={40}
              style={{
                backgroundColor: "#10b981",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                fontSize: "20px",
              }}
            >
              🧠
            </Avatar>

            <Flex vertical gap={2}>
              <Typography.Title
                level={4}
                style={{
                  color: "#ffffff",
                  margin: 0,
                  fontWeight: "bold",
                  fontSize: "18px",
                  lineHeight: "1.2",
                }}
              >
                DRIS.AI
              </Typography.Title>

              <Typography.Text
                style={{
                  color: "#71717a",
                  fontSize: "10px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                DIAGNOSE FOLIAR
              </Typography.Text>
            </Flex>
          </Flex>
        </div>

        <Typography.Text
          style={{
            color: "#71717a",
            fontSize: "10px",
            textTransform: "uppercase",
            letterSpacing: "0.5px",
            marginLeft: 16,
          }}
        >
          Navegação
        </Typography.Text>
        <Menu
          title="Navegação"
          theme="dark"
          mode="inline"
          selectedKeys={selecionado ? [selecionado] : []}
          items={itens}
        />
      </Sider>

      <Layout style={{ height: "100vh" }}>
        <Header
          style={{
            background: "#fff",
            borderBottom: "1px solid #f0f0f0",
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
            paddingInline: 24,
          }}
        >
          <Dropdown
            menu={{
              items: [
                { key: "perfil", icon: <UserOutlined />, label: "Meu perfil" },
                { type: "divider" },
                {
                  key: "sair",
                  icon: <LogoutOutlined />,
                  label: "Sair",
                  danger: true,
                },
              ],
              onClick: async ({ key }) => {
                if (key === "perfil") navigate("/perfil");
                if (key === "sair") {
                  await sair();
                  navigate("/login");
                }
              },
            }}
          >
            <div
              style={{
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <Avatar
                style={{ background: "#2e7d32" }}
                icon={<UserOutlined />}
              />
              <div style={{ lineHeight: 1.2 }}>
                <div style={{ fontWeight: 500 }}>{usuario?.nome}</div>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {usuario?.perfil === "ADMIN" ? "Administrador" : "Agrônomo"}
                </Typography.Text>
              </div>
            </div>
          </Dropdown>
        </Header>

        <Content style={{ padding: 24, overflowY: "auto" }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}