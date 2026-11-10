<?php
// 1. Conexión a SQLite mediante PDO
$db = new PDO('sqlite:portafolio.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Consultar los datos (Reporte 1: Últimos 30 días de Cierres para la Gráfica)
$query = "SELECT Date, Ticker, Close, Volatilidad_30d FROM historico_activos WHERE Date >= date('now', '-30 days') ORDER BY Date ASC";
$stmt = $db->query($query);
$datos = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Estructurar datos para JavaScript
$fechas = [];
$series = ['NVDA' => [], 'KO' => [], 'SLV' => []];

foreach ($datos as $row) {
    if (!in_array($row['Date'], $fechas)) {
        $fechas[] = $row['Date'];
    }
    $series[$row['Ticker']][] = $row['Close'];
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Financiero Automatizado</title>
    <!-- Incluir Chart.js para interactividad -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;}
        .canvas-container { height: 400px; }
    </style>
</head>
<body>

    <h2>Reporte 1: Rendimiento Histórico (Últimos 30 días)</h2>
    <div class="card canvas-container">
        <canvas id="rendimientoChart"></canvas>
    </div>

    <script>
        // Recibir los datos de PHP a JavaScript
        const fechas = <?php echo json_encode(array_values(array_unique($fechas))); ?>;
        const nvdaData = <?php echo json_encode($series['NVDA']); ?>;
        const koData = <?php echo json_encode($series['KO']); ?>;
        const slvData = <?php echo json_encode($series['SLV']); ?>;

        // Renderizar Reporte 1 con Chart.js
        const ctx = document.getElementById('rendimientoChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: fechas,
                datasets: [
                    { label: 'NVDA (Tecnología)', data: nvdaData, borderColor: '#76b900', tension: 0.1 },
                    { label: 'KO (Consumo)', data: koData, borderColor: '#f40009', tension: 0.1 },
                    { label: 'SLV (Plata)', data: slvData, borderColor: '#c0c0c0', tension: 0.1 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: 'Precios de Cierre Ajustados' }
                }
            }
        });
    </script>
</body>
</html>