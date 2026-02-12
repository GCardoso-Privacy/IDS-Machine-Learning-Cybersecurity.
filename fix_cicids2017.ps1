# =============================================================================
#  SCRIPT DE CORREÇÃO V2: CICIDS2017 (Link Validado)
# =============================================================================

$targetDir = "E:\Estudos_Cybersecurity\Datasets_Cybersecurity\CICIDS2017"
$zipFile   = Join-Path -Path $targetDir -ChildPath "MachineLearningCSV.zip"

# LINK JÁ VALIDADO PELO SMOKE TEST (Status 200 OK)
$url = "http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/CIC-IDS-2017/CSVs/MachineLearningCSV.zip"

# Configuração de TLS
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Clear-Host
Write-Host ">>> BAIXANDO CICIDS2017 (VERSÃO CORRIGIDA) <<<" -ForegroundColor Cyan
Write-Host "Destino: $targetDir" -ForegroundColor Gray

# 1. Garante estrutura de pastas e limpa tentativas falhas
if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir | Out-Null }
if (Test-Path $zipFile) { Remove-Item $zipFile -Force }

# 2. Download Otimizado (Sem warning de script)
try {
    Write-Host "Iniciando download de 224 MB... Aguarde." -ForegroundColor Yellow
    
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($url, $zipFile)
    
    if (Test-Path $zipFile) {
        $sizeMB = "{0:N2}" -f ((Get-Item $zipFile).Length / 1MB)
        Write-Host "Download Concluído ($sizeMB MB)!" -ForegroundColor Green
        
        # 3. Extração Automática
        Write-Host "Extraindo arquivos CSV..." -ForegroundColor Yellow
        Expand-Archive -Path $zipFile -DestinationPath $targetDir -Force
        
        # Limpeza do zip para economizar espaço
        Remove-Item $zipFile -Force
        
        Write-Host "`n>>> SUCESSO TOTAL! <<<" -ForegroundColor Cyan
        Write-Host "Os arquivos estão prontos em: $targetDir" -ForegroundColor Green
    }
}
catch {
    Write-Host "ERRO: $_" -ForegroundColor Red
}