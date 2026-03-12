<?php
/**
 * Plugin Name: Ecdótica Analyzer v2
 * Description: Analizador avanzado de manuscritos con RAG y LlamaIndex
 * Version: 2.0.0
 * Author: Editorial Nuevo Milenio
 */

// Configuración del API
define('ECDOTICA_API_BASE_URL', 'https://api.ecdotica.com/api/v1');

define('ECDOTICA_API_TIMEOUT', 300); // 5 minutos para análisis RAG

/**
 * Función principal para analizar manuscrito con RAG
 */
function ecdotica_analyze_manuscript_rag($file_path, $author = '', $title = '') {
    // Preparar el archivo para envío
    $file_data = array(
        'file' => new CURLFile($file_path, mime_content_type($file_path), basename($file_path)),
        'author' => $author,
        'title' => $title
    );
    
    // Inicializar cURL
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, ECDOTICA_API_BASE_URL . '/manuscripts/analyze-rag');
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $file_data);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, ECDOTICA_API_TIMEOUT);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Accept: application/json'
    ));
	    curl_setopt($ch, CURLOPT_BUFFERSIZE, 128 * 1024); // 128KB buffer
    curl_setopt($ch, CURLOPT_NOPROGRESS, false);
    
    // Ejecutar request
    $response = curl_exec($ch);
	    error_log('ECDOTICA DEBUG: Response length: ' . strlen($response));
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    // Procesar respuesta
    if ($error) {
        return array(
            'success' => false,
            'error' => 'Error de conexión: ' . $error
        );
    }
    
    if ($http_code !== 200) {
        return array(
            'success' => false,
            'error' => 'Error del servidor (código ' . $http_code . ')'
        );
    }
    
    $result = json_decode($response, true);
    if (!$result) {
        return array(
            'success' => false,
            'error' => 'Error al procesar la respuesta del servidor'
        );
    }
    
    return array(
        'success' => true,
        'data' => $result
    );
}

/**
 * Shortcode para mostrar el formulario de análisis
 */
function ecdotica_analyzer_shortcode() {
    ob_start();
    ?>
    <div id="ecdotica-analyzer-container">
        <style>
            #ecdotica-analyzer-container {
                max-width: 1000px;
                margin: 40px auto;
                padding: 30px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .ecdotica-form-group {
                margin-bottom: 20px;
            }
            .ecdotica-form-group label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #333;
            }
            .ecdotica-form-group input[type="text"],
            .ecdotica-form-group input[type="file"] {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            .ecdotica-submit-btn {
                background: #2271b1;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 16px;
                border-radius: 4px;
                cursor: pointer;
                transition: background 0.3s;
            }
            .ecdotica-submit-btn:hover {
                background: #135e96;
            }
            .ecdotica-submit-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            #ecdotica-loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #666;
            }
            #ecdotica-results {
                display: none;
                margin-top: 30px;
            }
            .ecdotica-result-section {
                margin-bottom: 25px;
                padding: 20px;
                background: #f8f9fa;
                border-left: 4px solid #2271b1;
                border-radius: 4px;
            }
            .ecdotica-result-section h3 {
                margin-top: 0;
                color: #2271b1;
                font-size: 18px;
            }
            .ecdotica-result-section p {
                line-height: 1.6;
                color: #333;
            }
            .ecdotica-error {
                padding: 15px;
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                border-radius: 4px;
                color: #721c24;
                margin-top: 20px;
            }
        </style>

        <h2>Analizador de Manuscritos con IA</h2>
        <p>Sube tu manuscrito en formato PDF para obtener un análisis literario profundo utilizando IA.</p>

        <form id="ecdotica-analyzer-form" enctype="multipart/form-data">
            <div class="ecdotica-form-group">
                <label for="manuscript-file">Archivo del manuscrito (PDF) *</label>
                <input type="file" id="manuscript-file" name="manuscript_file" accept=".pdf" required>
            </div>

            <div class="ecdotica-form-group">
                <label for="manuscript-author">Autor (opcional)</label>
                <input type="text" id="manuscript-author" name="author" placeholder="Nombre del autor">
            </div>

            <div class="ecdotica-form-group">
                <label for="manuscript-title">Título (opcional)</label>
                <input type="text" id="manuscript-title" name="title" placeholder="Título del manuscrito">
            </div>

            <button type="submit" class="ecdotica-submit-btn">Analizar Manuscrito</button>
        </form>

        <div id="ecdotica-loading">
            <p>⏳ Analizando manuscrito... Este proceso puede tomar varios minutos.</p>
        </div>

        <div id="ecdotica-results"></div>
    </div>

    <script>
    jQuery(document).ready(function($) {
        $('#ecdotica-analyzer-form').on('submit', function(e) {
            e.preventDefault();
            
            const fileInput = $('#manuscript-file')[0];
            if (!fileInput.files.length) {
                alert('Por favor selecciona un archivo PDF');
                return;
            }

            const formData = new FormData();
            formData.append('action', 'ecdotica_analyze_rag');
            formData.append('manuscript_file', fileInput.files[0]);
            formData.append('author', $('#manuscript-author').val());
            formData.append('title', $('#manuscript-title').val());

            // Mostrar loading
            $('#ecdotica-loading').show();
            $('#ecdotica-results').hide();
            $('.ecdotica-submit-btn').prop('disabled', true);

            $.ajax({
                url: '<?php echo admin_url('admin-ajax.php'); ?>',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                timeout: 300000, // 5 minutos
                success: function(response) {
                    $('#ecdotica-loading').hide();
                    $('.ecdotica-submit-btn').prop('disabled', false);

                    if (response.success) {
                        displayResults(response.data);
                    } else {
                        displayError(response.data || 'Error desconocido');
                    }
                },
                error: function(xhr, status, error) {
                    $('#ecdotica-loading').hide();
                    $('.ecdotica-submit-btn').prop('disabled', false);
                    displayError('Error de conexión: ' + error);
                }
            });
        });

        function displayResults(data) {
            let html = '<h3>Resultados del Análisis</h3>';
            
            if (data.statistics) {
                html += '<div class="ecdotica-result-section">';
                html += '<h3>📊 Estadísticas Generales</h3>';
                html += '<p><strong>Palabras:</strong> ' + (data.statistics.word_count || 'N/A') + '</p>';
                html += '<p><strong>ID del manuscrito:</strong> ' + (data.manuscript_id || 'N/A') + '</p>';
                html += '</div>';
            }

            const analysis = data.analysis || {};
            
            const sections = [
                { key: 'style', title: '✍️ Análisis de Estilo', icon: '✍️' },
                { key: 'structure', title: '🏗️ Estructura Narrativa', icon: '🏗️' },
                { key: 'characters', title: '👥 Desarrollo de Personajes', icon: '👥' },
                { key: 'themes', title: '🎭 Temas y Motivos', icon: '🎭' },
                { key: 'language', title: '📝 Uso del Lenguaje', icon: '📝' },
                { key: 'marketability', title: '📈 Potencial Editorial', icon: '📈' },
                { key: 'recommendations', title: '💡 Recomendaciones', icon: '💡' }
            ];

            sections.forEach(function(section) {
                if (analysis[section.key]) {
                    html += '<div class="ecdotica-result-section">';
                    html += '<h3>' + section.title + '</h3>';
                    html += '<p>' + analysis[section.key] + '</p>';
                    html += '</div>';
                }
            });

            
			        // FIX: Convertir "X/10" a "X%" en el HTML antes de insertar
        html = html.replace(/(\d+(?:\.\d+)?)\/10/g, function(match, num) {
            return (parseFloat(num) * 10) + '%';
        });
        $('#ecdotica-results').html(html).show();
        }

        function displayError(message) {
            const html = '<div class="ecdotica-error">⚠️ ' + message + '</div>';
            $('#ecdotica-results').html(html).show();
        }
    });
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('ecdotica_analyzer', 'ecdotica_analyzer_shortcode');

/**
 * Handler AJAX para el análisis
 */
function ecdotica_ajax_analyze_rag() {
    // Verificar que se subió un archivo
    if (!isset($_FILES['manuscript_file'])) {
        wp_send_json_error('No se recibió ningún archivo');
        return;
    }

    $file = $_FILES['manuscript_file'];
    
    // Validar que es un PDF
    if ($file['type'] !== 'application/pdf') {
        wp_send_json_error('El archivo debe ser un PDF');
        return;
    }

    // Obtener datos adicionales
    $author = isset($_POST['author']) ? sanitize_text_field($_POST['author']) : '';
    $title = isset($_POST['title']) ? sanitize_text_field($_POST['title']) : '';

    // Analizar el manuscrito
    $result = ecdotica_analyze_manuscript_rag($file['tmp_name'], $author, $title);

    if ($result['success']) {
        wp_send_json_success($result['data']);
    } else {
        wp_send_json_error($result['error']);
    }
}
add_action('wp_ajax_ecdotica_analyze_rag', 'ecdotica_ajax_analyze_rag');
add_action('wp_ajax_nopriv_ecdotica_analyze_rag', 'ecdotica_ajax_analyze_rag');
// Registrar menú de Ecdotica
add_action('admin_menu', 'ecdotica_add_admin_menu');

function ecdotica_add_admin_menu() {
    add_menu_page(
        'Ecdotica - Análisis de Manuscritos',
        'Ecdotica',
        'manage_options',
        'ecdotica-analyzer',
        'ecdotica_render_admin_page',
        'dashicons-analytics',
        30
    );
}

function ecdotica_render_admin_page() {
    ?>
    <div class="wrap">
        <h1>Ecdotica - Análisis de Manuscritos</h1>
        <div class="ecdotica-container">
            <form id="ecdotica-upload-form" method="post" enctype="multipart/form-data">
                <?php wp_nonce_field('ecdotica_upload', 'ecdotica_nonce'); ?>
                
                <table class="form-table">
                    <tr>
                        <th scope="row"><label for="manuscript_file">Archivo del manuscrito:</label></th>
                        <td>
                            <input type="file" name="manuscript_file" id="manuscript_file" accept=".docx,.pdf,.txt" required />
                            <p class="description">Formatos aceptados: Word (.docx), PDF (.pdf), Texto (.txt)</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="author_name">Autor:</label></th>
                        <td><input type="text" name="author_name" id="author_name" class="regular-text" /></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="manuscript_title">Título:</label></th>
                        <td><input type="text" name="manuscript_title" id="manuscript_title" class="regular-text" /></td>
                    </tr>
                </table>
                
                <p class="submit">
                    <button type="submit" class="button button-primary" id="ecdotica-submit-btn">
                        <span class="dashicons dashicons-upload"></span> Analizar Manuscrito
                    </button>
                </p>
            </form>
            
            <div id="ecdotica-results" style="display:none; margin-top: 30px;">
                <h2>Resultados del Análisis</h2>
                <div id="ecdotica-results-content"></div>
            </div>
        </div>
    </div>
    
    <style>
        .ecdotica-container { max-width: 800px; }
        #ecdotica-results { background: #f0f0f1; padding: 20px; border-radius: 4px; }
        .ecdotica-score { font-size: 24px; font-weight: bold; margin: 10px 0; }
    </style>
    
    <script type="text/javascript">
    jQuery(document).ready(function($) {
        $('#ecdotica-upload-form').on('submit', function(e) {
            e.preventDefault();
            
            var formData = new FormData(this);
            formData.append('action', 'ecdotica_ajax_analyze_rag');
            
            $('#ecdotica-submit-btn').prop('disabled', true).text('Analizando...');
            $('#ecdotica-results').hide();
            
            $.ajax({
                url: ajaxurl,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    $('#ecdotica-submit-btn').prop('disabled', false).html('<span class="dashicons dashicons-upload"></span> Analizar Manuscrito');
                    
                    if (response.success) {
                        var data = response.data;
                        var html = '<div class="ecdotica-score">Calidad: ' + data.quality_score + '/10</div>';
                        html += '<p><strong>Decisión Editorial:</strong> ' + data.editorial_decision + '</p>';
                        html += '<p><strong>Recomendación:</strong> ' + data.recommendation + '</p>';
                        html += '<h3>Análisis Detallado:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                        
                        $('#ecdotica-results-content').html(html);
                        $('#ecdotica-results').show();
                    } else {
                        alert('Error: ' + response.data);
                    }
                },
                error: function() {
                    $('#ecdotica-submit-btn').prop('disabled', false).html('<span class="dashicons dashicons-upload"></span> Analizar Manuscrito');
                    alert('Error de conexión con el servidor.');
                }
            });
        });
    });
    </script>
    <script>
    // FIX: Convertir valores con formato "X/10" a porcentaje "X*10%"
    function fixPlagiarismPercentage() {
        // Buscar todos los elementos de texto en el modal de resultados
        const modal = document.querySelector('#ecdotica-results');
        if (!modal) return;

        // Recorrer todos los nodos de texto y reemplazar "X/10" por "X*10%"
        const walker = document.createTreeWalker(
            modal,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        while (node = walker.nextNode()) {
            if (node.textContent && node.textContent.match(/\d+(?:\.\d+)?\/10/)) {
                node.textContent = node.textContent.replace(/([\d.]+)\/10/g, function(match, num) {
                    return (parseFloat(num) * 10) + '%';
                });
            }
        }
    }

    // Ejecutar el fix después de que se muestren los resultados
    // Usar MutationObserver para detectar cuando el modal se muestra
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                const modal = document.querySelector('#ecdotica-results');
                if (modal && modal.style.display !== 'none') {
                    setTimeout(fixPlagiarismPercentage, 10);
                }
            }
        });
    });

    // Observar cambios en el modal
    const resultsModal = document.querySelector('#ecdotica-results');
    if (resultsModal) {
        observer.observe(resultsModal, { attributes: true });
    }
    </script>
    <?php }

// ============================================
// AJAX HANDLERS PARA REPORTES
// ============================================

// AJAX handler para generar reporte Word
add_action('wp_ajax_ecdotica_generate_word_report', 'ecdotica_generate_word_report_ajax');

function ecdotica_generate_word_report_ajax() {
    check_ajax_referer('ecdotica_word_nonce', 'nonce');

    if (!isset($_POST['analysis_data'])) {
        wp_send_json_error(['message' => 'No hay datos de análisis']);
    }

    $analysis_data = json_decode(stripslashes($_POST['analysis_data']), true);

    if (!$analysis_data) {
        wp_send_json_error(['message' => 'Datos de análisis inválidos']);
    }

    // Incluir el generador de reportes
    require_once plugin_dir_path(__FILE__) . 'word-report-generator.php';

    // Generar el reporte
    $generator = new Ecdotica_Word_Report_Generator();
    $filepath = $generator->generate_report($analysis_data);

    if (is_wp_error($filepath)) {
        wp_send_json_error(['message' => $filepath->get_error_message()]);
    }

    // Obtener URL de descarga
    $upload_dir = wp_upload_dir();
    $upload_url = $upload_dir['baseurl'];
    $relative_path = str_replace($upload_dir['basedir'], '', $filepath);
    $download_url = $upload_url . $relative_path;

    wp_send_json_success([
        'download_url' => $download_url,
        'filename' => basename($filepath)
    ]);
}

// AJAX handler para generar reporte PDF
add_action('wp_ajax_ecdotica_generate_pdf_report', 'ecdotica_generate_pdf_report_ajax');

function ecdotica_generate_pdf_report_ajax() {
    check_ajax_referer('ecdotica_pdf_nonce', 'nonce');

    if (!isset($_POST['analysis_data'])) {
        wp_send_json_error(['message' => 'No hay datos de análisis']);
    }

    $analysis_data = json_decode(stripslashes($_POST['analysis_data']), true);

    if (!$analysis_data) {
        wp_send_json_error(['message' => 'Datos de análisis inválidos']);
    }

    // Incluir el generador de reportes PDF
    require_once plugin_dir_path(__FILE__) . 'pdf-report-generator.php';

    // Generar el reporte PDF
    $generator = new Ecdotica_PDF_Report_Generator();
    $filepath = $generator->generate_report($analysis_data);

    if (is_wp_error($filepath)) {
        wp_send_json_error(['message' => $filepath->get_error_message()]);
    }

    // Obtener URL de descarga
    $download_url = $generator->get_download_url($filepath);

    wp_send_json_success([
        'download_url' => $download_url,
        'filename' => basename($filepath),
        'message' => 'Reporte PDF generado exitosamente'
    ]);
}
