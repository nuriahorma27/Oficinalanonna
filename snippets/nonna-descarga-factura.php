// Nonna: acceso privado para descargar la factura de un pedido (la usa n8n).
// Solo responde con una clave de la API de WooCommerce con permiso de lectura.
add_action( 'rest_api_init', function () {
	register_rest_route( 'wc/v3', '/nonna-factura/(?P<id>\d+)', array(
		'methods'             => 'GET',
		'permission_callback' => function () {
			return current_user_can( 'manage_woocommerce' );
		},
		'callback'            => function ( $request ) {
			try {
				if ( ! function_exists( 'wcpdf_get_document' ) ) {
					return new WP_Error( 'nonna_sin_plugin', 'El plugin de facturas no esta disponible.', array( 'status' => 500 ) );
				}
				$order = wc_get_order( (int) $request['id'] );
				if ( ! $order ) {
					return new WP_Error( 'nonna_sin_pedido', 'Pedido no encontrado.', array( 'status' => 404 ) );
				}
				// Sin crear nada: solo devuelve la factura si ya existe.
				$invoice = wcpdf_get_document( 'invoice', $order );
				if ( ! $invoice ) {
					return new WP_Error( 'nonna_sin_factura', 'Este pedido no tiene factura.', array( 'status' => 404 ) );
				}
				$pdf = $invoice->get_pdf();
				if ( ! $pdf ) {
					return new WP_Error( 'nonna_sin_pdf', 'No se pudo generar el PDF.', array( 'status' => 500 ) );
				}
				$numero = $invoice->get_number( 'invoice' );
				return rest_ensure_response( array(
					'order_id'       => $order->get_id(),
					'invoice_number' => $numero ? $numero->get_formatted() : '',
					'filename'       => $invoice->get_filename(),
					'pdf_base64'     => base64_encode( $pdf ),
				) );
			} catch ( \Throwable $e ) {
				return new WP_Error( 'nonna_error', 'Error al generar la factura.', array( 'status' => 500 ) );
			}
		},
	) );
} );
