import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthContext'
import { AppLayout } from '@/app/layout/AppLayout'
import { RoleGuard } from '@/app/routes/RoleGuard'
import { LoginPage } from '@/features/auth/LoginPage'
import { CadastroPage } from '@/features/auth/CadastroPage'
import { PerfilPage } from '@/features/perfil/PerfilPage'
import { NormasPage } from '@/features/normas/NormasPage'
import { InsumosPage } from '@/features/insumos/InsumosPage'
import { ProdutoresPage } from '@/features/produtores/ProdutoresPage'
import { PropriedadesPage } from '@/features/propriedades/PropriedadesPage'
import { TalhoesPage } from '@/features/talhoes/TalhoesPage'
import { AmostrasPage } from '@/features/amostras/AmostrasPage'
import { ResultadosPage } from '@/features/amostras/ResultadosPage'

/** Página inicial de cada perfil (RF003). */
function RotaInicial() {
  const { usuario } = useAuth()
  return <Navigate to={usuario?.perfil === 'ADMIN' ? '/normas' : '/produtores'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/cadastro" element={<CadastroPage />} />

      <Route element={<RoleGuard />}>
        <Route element={<AppLayout />}>
          <Route index element={<RotaInicial />} />
          <Route path="/perfil" element={<PerfilPage />} />

          <Route element={<RoleGuard perfis={['ADMIN']} />}>
            <Route path="/normas" element={<NormasPage />} />
            <Route path="/insumos" element={<InsumosPage />} />
          </Route>

          <Route element={<RoleGuard perfis={['AGRONOMO']} />}>
            <Route path="/produtores" element={<ProdutoresPage />} />
            <Route path="/propriedades" element={<PropriedadesPage />} />
            <Route path="/talhoes" element={<TalhoesPage />} />
            <Route path="/amostras" element={<AmostrasPage />} />
            <Route path="/amostras/:id" element={<ResultadosPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
