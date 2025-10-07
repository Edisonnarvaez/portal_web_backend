# API Documentation - Portal Web Backend

## Documentación OpenAPI/Swagger

Esta documentación describe la API REST completa del Portal Web Backend utilizando la especificación OpenAPI 3.0.

---

## Especificación OpenAPI 3.0

```yaml
openapi: 3.0.3
info:
  title: Portal Web Backend API
  description: |
    API REST completa para el sistema de gestión integral Portal Web Backend.
    
    Características principales:
    - Sistema de gestión de proveedores y facturación electrónica
    - Autenticación JWT con 2FA
    - Gestión de empresas, departamentos y sedes
    - Sistema de indicadores y métricas
    - Gestión de auditorías y procesos
    
    ## Autenticación
    
    Esta API utiliza autenticación JWT (JSON Web Tokens) con autenticación de dos factores opcional.
    
    ### Flujo de Autenticación:
    1. Obtener token mediante `/api/token/` con credenciales
    2. Para usuarios con 2FA habilitado, verificar código con `/api/users/verify-2fa/`
    3. Usar el token JWT en el header `Authorization: Bearer <token>`
    4. Refrescar token usando `/api/token/refresh/`
    
    ## Códigos de Estado
    
    - `200` - Éxito
    - `201` - Recurso creado exitosamente  
    - `400` - Error de validación
    - `401` - No autenticado
    - `403` - Sin permisos
    - `404` - Recurso no encontrado
    - `500` - Error interno del servidor
    
  version: 1.0.0
  contact:
    name: Equipo de Desarrollo Portal Web Backend
    email: desarrollo@portalweb.com
  license:
    name: Propietario
    
servers:
  - url: http://127.0.0.1:8000/api
    description: Servidor de desarrollo
  - url: http://127.0.0.1:8081/api  
    description: Servidor de producción local
  - url: https://red.redmedicronips.com.co/api
    description: Servidor de producción

security:
  - BearerAuth: []

paths:
  # =============================================================================
  # AUTENTICACIÓN
  # =============================================================================
  
  /token/:
    post:
      tags:
        - Autenticación
      summary: Obtener token JWT
      description: Autenticar usuario y obtener tokens de acceso y refresh
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: Nombre de usuario o email
                  example: "admin@example.com"
                password:
                  type: string
                  format: password
                  description: Contraseña del usuario
                  example: "password123"
              required:
                - username
                - password
      responses:
        '200':
          description: Autenticación exitosa
          content:
            application/json:
              schema:
                type: object
                properties:
                  access:
                    type: string
                    description: Token JWT de acceso
                  refresh:
                    type: string
                    description: Token JWT para refresh
        '401':
          $ref: '#/components/responses/Unauthorized'

  /token/refresh/:
    post:
      tags:
        - Autenticación
      summary: Refrescar token JWT
      description: Obtener nuevo token de acceso usando refresh token
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                refresh:
                  type: string
                  description: Token de refresh válido
              required:
                - refresh
      responses:
        '200':
          description: Token refrescado exitosamente
          content:
            application/json:
              schema:
                type: object
                properties:
                  access:
                    type: string
                    description: Nuevo token JWT de acceso
        '401':
          $ref: '#/components/responses/Unauthorized'

  # =============================================================================
  # USUARIOS
  # =============================================================================

  /users/register/:
    post:
      tags:
        - Usuarios
      summary: Registrar nuevo usuario
      description: Crear una nueva cuenta de usuario
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserRegistration'
      responses:
        '201':
          description: Usuario creado exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/ValidationError'

  /users/login/:
    post:
      tags:
        - Usuarios
      summary: Iniciar sesión
      description: Iniciar sesión con credenciales de usuario. Si el usuario tiene 2FA habilitado, se enviará un código por email.
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: "admin@example.com"
                password:
                  type: string
                  format: password
                  example: "password123"
              required:
                - username
                - password
      responses:
        '200':
          description: Login exitoso
          content:
            application/json:
              schema:
                oneOf:
                  - type: object
                    properties:
                      access:
                        type: string
                      refresh:
                        type: string
                      user:
                        $ref: '#/components/schemas/User'
                  - type: object
                    properties:
                      message:
                        type: string
                        example: "Código 2FA enviado por email"
                      requires_2fa:
                        type: boolean
                        example: true
        '401':
          $ref: '#/components/responses/Unauthorized'

  /users/verify-2fa/:
    post:
      tags:
        - Usuarios
      summary: Verificar código 2FA
      description: Verificar código de autenticación de dos factores
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: "admin@example.com"
                code:
                  type: string
                  example: "123456"
              required:
                - username
                - code
      responses:
        '200':
          description: 2FA verificado exitosamente
          content:
            application/json:
              schema:
                type: object
                properties:
                  access:
                    type: string
                  refresh:
                    type: string
                  user:
                    $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/ValidationError'

  /users/profile/:
    get:
      tags:
        - Usuarios
      summary: Obtener perfil del usuario
      description: Obtener información del perfil del usuario autenticado
      responses:
        '200':
          description: Perfil del usuario
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '401':
          $ref: '#/components/responses/Unauthorized'
    
    put:
      tags:
        - Usuarios
      summary: Actualizar perfil del usuario
      description: Actualizar información del perfil del usuario autenticado
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserUpdate'
      responses:
        '200':
          description: Perfil actualizado exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/ValidationError'

  # =============================================================================
  # EMPRESAS
  # =============================================================================

  /companies/companies/:
    get:
      tags:
        - Empresas
      summary: Listar empresas
      description: Obtener lista de empresas registradas
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
        - name: search
          in: query
          description: Buscar por nombre o NIT
          schema:
            type: string
      responses:
        '200':
          description: Lista de empresas
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedCompanyList'

    post:
      tags:
        - Empresas
      summary: Crear empresa
      description: Registrar una nueva empresa
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CompanyInput'
      responses:
        '201':
          description: Empresa creada exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Company'
        '400':
          $ref: '#/components/responses/ValidationError'

  /companies/companies/{id}/:
    get:
      tags:
        - Empresas
      summary: Obtener empresa por ID
      description: Obtener información detallada de una empresa
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Información de la empresa
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Company'
        '404':
          $ref: '#/components/responses/NotFound'

    put:
      tags:
        - Empresas
      summary: Actualizar empresa
      description: Actualizar información completa de una empresa
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CompanyInput'
      responses:
        '200':
          description: Empresa actualizada exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Company'
        '400':
          $ref: '#/components/responses/ValidationError'
        '404':
          $ref: '#/components/responses/NotFound'

    delete:
      tags:
        - Empresas
      summary: Eliminar empresa
      description: Eliminar una empresa del sistema
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '204':
          description: Empresa eliminada exitosamente
        '404':
          $ref: '#/components/responses/NotFound'

  # =============================================================================
  # GESTIÓN DE PROVEEDORES - FACTURAS
  # =============================================================================

  /gestionProveedores/facturas/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Listar facturas
      description: Obtener lista de facturas con filtros opcionales
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
        - name: etapa
          in: query
          description: Filtrar por etapa del proceso
          schema:
            type: string
            enum: ["etapa1", "etapa2", "etapa3", "etapa4", "etapa5", "etapa6"]
        - name: estado
          in: query
          description: Filtrar por estado de factura
          schema:
            type: integer
        - name: fecha_desde
          in: query
          description: Filtrar facturas desde esta fecha
          schema:
            type: string
            format: date
        - name: fecha_hasta
          in: query
          description: Filtrar facturas hasta esta fecha
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Lista de facturas
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedFacturaList'

    post:
      tags:
        - Gestión de Proveedores
      summary: Crear factura
      description: Registrar una nueva factura en el sistema
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/FacturaInput'
      responses:
        '201':
          description: Factura creada exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Factura'
        '400':
          $ref: '#/components/responses/ValidationError'

  /gestionProveedores/facturas/{id}/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Obtener factura por ID
      description: Obtener información detallada de una factura
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Información de la factura
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Factura'
        '404':
          $ref: '#/components/responses/NotFound'

  /gestionProveedores/etapa1-gestionar-fe/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Facturas en Etapa 1 - Gestionar FE
      description: Obtener facturas en la primera etapa del proceso (Gestión de Factura Electrónica)
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
      responses:
        '200':
          description: Facturas en etapa 1
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedFacturaList'

  /gestionProveedores/etapa2-pendiente-revision/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Facturas en Etapa 2 - Pendiente Revisión
      description: Obtener facturas en la segunda etapa del proceso (Pendiente de Revisión)
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
      responses:
        '200':
          description: Facturas en etapa 2
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedFacturaList'

  /gestionProveedores/etapa3-pendiente-reconocimiento-contable/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Facturas en Etapa 3 - Reconocimiento Contable
      description: Obtener facturas en la tercera etapa del proceso (Pendiente Reconocimiento Contable)
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
      responses:
        '200':
          description: Facturas en etapa 3
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedFacturaList'

  /gestionProveedores/etapa4-revision-impuestos/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Facturas en Etapa 4 - Revisión Impuestos
      description: Obtener facturas en la cuarta etapa del proceso (Revisión de Impuestos)
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
      responses:
        '200':
          description: Facturas en etapa 4
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedFacturaList'

  /gestionProveedores/etapa5-revision-contraloria/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Facturas en Etapa 5 - Revisión Contraloría
      description: Obtener facturas en la quinta etapa del proceso (Revisión Contraloría)
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
      responses:
        '200':
          description: Facturas en etapa 5
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedFacturaList'

  /gestionProveedores/etapa6-pendiente-pago/:
    get:
      tags:
        - Gestión de Proveedores
      summary: Facturas en Etapa 6 - Pendiente Pago
      description: Obtener facturas en la sexta etapa del proceso (Pendiente de Pago)
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
      responses:
        '200':
          description: Facturas en etapa 6
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedFacturaList'

  # =============================================================================
  # TERCEROS
  # =============================================================================

  /terceros/terceros/:
    get:
      tags:
        - Terceros
      summary: Listar terceros
      description: Obtener lista de terceros registrados
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
        - name: search
          in: query
          description: Buscar por nombre o documento
          schema:
            type: string
      responses:
        '200':
          description: Lista de terceros
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedTerceroList'

    post:
      tags:
        - Terceros
      summary: Crear tercero
      description: Registrar un nuevo tercero
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TerceroInput'
      responses:
        '201':
          description: Tercero creado exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Tercero'
        '400':
          $ref: '#/components/responses/ValidationError'

  /terceros/paises/:
    get:
      tags:
        - Terceros
      summary: Listar países
      description: Obtener lista de países disponibles
      responses:
        '200':
          description: Lista de países
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Pais'

  /terceros/departamentos/:
    get:
      tags:
        - Terceros
      summary: Listar departamentos
      description: Obtener lista de departamentos, opcionalmente filtrados por país
      parameters:
        - name: pais
          in: query
          description: ID del país para filtrar departamentos
          schema:
            type: integer
      responses:
        '200':
          description: Lista de departamentos
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Departamento'

  /terceros/municipios/:
    get:
      tags:
        - Terceros
      summary: Listar municipios
      description: Obtener lista de municipios, opcionalmente filtrados por departamento
      parameters:
        - name: departamento
          in: query
          description: ID del departamento para filtrar municipios
          schema:
            type: integer
      responses:
        '200':
          description: Lista de municipios
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Municipio'

  # =============================================================================
  # INDICADORES
  # =============================================================================

  /indicators/indicators/:
    get:
      tags:
        - Indicadores
      summary: Listar indicadores
      description: Obtener lista de indicadores configurados
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
      responses:
        '200':
          description: Lista de indicadores
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedIndicatorList'

    post:
      tags:
        - Indicadores
      summary: Crear indicador
      description: Crear un nuevo indicador
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IndicatorInput'
      responses:
        '201':
          description: Indicador creado exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Indicator'
        '400':
          $ref: '#/components/responses/ValidationError'

  /indicators/results/:
    get:
      tags:
        - Indicadores
      summary: Listar resultados de indicadores
      description: Obtener resultados de indicadores con filtros opcionales
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
        - name: indicator
          in: query
          description: ID del indicador
          schema:
            type: integer
        - name: headquarters
          in: query
          description: ID de la sede
          schema:
            type: integer
        - name: period_start
          in: query
          description: Inicio del período
          schema:
            type: string
            format: date
        - name: period_end
          in: query
          description: Final del período
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Lista de resultados
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedResultList'

    post:
      tags:
        - Indicadores
      summary: Crear resultado de indicador
      description: Registrar un nuevo resultado para un indicador
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ResultInput'
      responses:
        '201':
          description: Resultado creado exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Result'
        '400':
          $ref: '#/components/responses/ValidationError'

# =============================================================================
# COMPONENTES REUTILIZABLES
# =============================================================================

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  parameters:
    PageParam:
      name: page
      in: query
      description: Número de página
      schema:
        type: integer
        default: 1
        minimum: 1
    
    PageSizeParam:
      name: page_size
      in: query
      description: Número de elementos por página
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100

  schemas:
    # =============================================================================
    # ESQUEMAS DE USUARIO
    # =============================================================================
    
    User:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        email:
          type: string
          format: email
        first_name:
          type: string
          maxLength: 150
        last_name:
          type: string  
          maxLength: 150
        is_active:
          type: boolean
          readOnly: true
        date_joined:
          type: string
          format: date-time
          readOnly: true
        roles:
          type: array
          items:
            $ref: '#/components/schemas/Role'
        profile:
          $ref: '#/components/schemas/UserProfile'

    UserRegistration:
      type: object
      required:
        - email
        - password
        - first_name
        - last_name
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          format: password
          minLength: 8
        first_name:
          type: string
          maxLength: 150
        last_name:
          type: string
          maxLength: 150

    UserUpdate:
      type: object
      properties:
        first_name:
          type: string
          maxLength: 150
        last_name:
          type: string
          maxLength: 150
        profile:
          $ref: '#/components/schemas/UserProfileUpdate'

    UserProfile:
      type: object
      properties:
        phone:
          type: string
          maxLength: 20
        address:
          type: string
          maxLength: 255
        birth_date:
          type: string
          format: date
        profile_picture:
          type: string
          format: uri
        two_factor_enabled:
          type: boolean

    UserProfileUpdate:
      type: object
      properties:
        phone:
          type: string
          maxLength: 20
        address:
          type: string
          maxLength: 255
        birth_date:
          type: string
          format: date
        two_factor_enabled:
          type: boolean

    Role:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 100
        description:
          type: string
        apps:
          type: array
          items:
            $ref: '#/components/schemas/App'

    App:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 100
        description:
          type: string

    # =============================================================================
    # ESQUEMAS DE EMPRESA
    # =============================================================================

    Company:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        nit:
          type: string
          maxLength: 50
        legalRepresentative:
          type: string
          maxLength: 255
        phone:
          type: string
          maxLength: 50
        address:
          type: string
          maxLength: 255
        contactEmail:
          type: string
          format: email
        foundationDate:
          type: string
          format: date
        status:
          type: boolean
        creationDate:
          type: string
          format: date
          readOnly: true
        updateDate:
          type: string
          format: date
          readOnly: true

    CompanyInput:
      type: object
      required:
        - name
        - nit
        - legalRepresentative
        - contactEmail
        - foundationDate
      properties:
        name:
          type: string
          maxLength: 255
        nit:
          type: string
          maxLength: 50
        legalRepresentative:
          type: string
          maxLength: 255
        phone:
          type: string
          maxLength: 50
        address:
          type: string
          maxLength: 255
        contactEmail:
          type: string
          format: email
        foundationDate:
          type: string
          format: date
        status:
          type: boolean
          default: true

    # =============================================================================
    # ESQUEMAS DE FACTURA
    # =============================================================================

    Factura:
      type: object
      properties:
        factura_id:
          type: integer
          readOnly: true
        factura_id_factura_electronica:
          type: string
          maxLength: 100
        factura_etapa:
          type: string
          maxLength: 50
          enum: ["etapa1", "etapa2", "etapa3", "etapa4", "etapa5", "etapa6"]
        factura_fecha:
          type: string
          format: date
        factura_numero_autorizacion:
          type: string
          maxLength: 100
        factura_concepto:
          type: string
        factura_razon_social_proveedor:
          type: string
          maxLength: 150
        factura_razon_social_adquiriente:
          type: string
          maxLength: 150
        factura_valor:
          type: number
          format: decimal
        factura_estado:
          type: boolean
        factura_centro_operaciones:
          $ref: '#/components/schemas/CentroOperaciones'
        factura_centro_costo:
          $ref: '#/components/schemas/CentroCostos'
        factura_estado_factura:
          $ref: '#/components/schemas/EstadoFactura'

    FacturaInput:
      type: object
      required:
        - factura_fecha
        - factura_valor
        - factura_concepto
      properties:
        factura_id_factura_electronica:
          type: string
          maxLength: 100
        factura_fecha:
          type: string
          format: date
        factura_numero_autorizacion:
          type: string
          maxLength: 100
        factura_concepto:
          type: string
        factura_razon_social_proveedor:
          type: string
          maxLength: 150
        factura_razon_social_adquiriente:
          type: string
          maxLength: 150
        factura_valor:
          type: number
          format: decimal
        factura_centro_operaciones:
          type: integer
        factura_centro_costo:
          type: integer
        archivo_factura:
          type: string
          format: binary
          description: Archivo PDF de la factura

    EstadoFactura:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        nombre:
          type: string
          maxLength: 100
        descripcion:
          type: string

    CentroOperaciones:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        nombre:
          type: string
          maxLength: 100
        codigo:
          type: string
          maxLength: 20

    CentroCostos:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        nombre:
          type: string
          maxLength: 100
        codigo:
          type: string
          maxLength: 20

    # =============================================================================
    # ESQUEMAS DE TERCEROS
    # =============================================================================

    Tercero:
      type: object
      properties:
        tercero_id:
          type: integer
          readOnly: true
        tercero_nombre:
          type: string
          maxLength: 255
        tercero_documento:
          type: string
          maxLength: 50
        tercero_telefono:
          type: string
          maxLength: 20
        tercero_email:
          type: string
          format: email
        tercero_direccion:
          type: string
          maxLength: 255
        tercero_municipio:
          $ref: '#/components/schemas/Municipio'

    TerceroInput:
      type: object
      required:
        - tercero_nombre
        - tercero_documento
        - tercero_municipio
      properties:
        tercero_nombre:
          type: string
          maxLength: 255
        tercero_documento:
          type: string
          maxLength: 50
        tercero_telefono:
          type: string
          maxLength: 20
        tercero_email:
          type: string
          format: email
        tercero_direccion:
          type: string
          maxLength: 255
        tercero_municipio:
          type: integer

    Pais:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        nombre:
          type: string
          maxLength: 100
        codigo:
          type: string
          maxLength: 10

    Departamento:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        nombre:
          type: string
          maxLength: 100
        codigo:
          type: string
          maxLength: 10
        pais:
          $ref: '#/components/schemas/Pais'

    Municipio:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        nombre:
          type: string
          maxLength: 100
        codigo:
          type: string
          maxLength: 10
        departamento:
          $ref: '#/components/schemas/Departamento'

    # =============================================================================
    # ESQUEMAS DE INDICADORES
    # =============================================================================

    Indicator:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        description:
          type: string
        measurement_unit:
          type: string
          maxLength: 50
        target_value:
          type: number
          format: decimal
        frequency:
          type: string
          enum: ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"]
        is_active:
          type: boolean
        created_at:
          type: string
          format: date-time
          readOnly: true
        process:
          $ref: '#/components/schemas/Process'

    IndicatorInput:
      type: object
      required:
        - name
        - measurement_unit
        - frequency
        - process
      properties:
        name:
          type: string
          maxLength: 255
        description:
          type: string
        measurement_unit:
          type: string
          maxLength: 50
        target_value:
          type: number
          format: decimal
        frequency:
          type: string
          enum: ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"]
        process:
          type: integer

    Result:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        value:
          type: number
          format: decimal
        period_start:
          type: string
          format: date
        period_end:
          type: string
          format: date
        notes:
          type: string
        created_at:
          type: string
          format: date-time
          readOnly: true
        indicator:
          $ref: '#/components/schemas/Indicator'
        headquarters:
          $ref: '#/components/schemas/Headquarters'

    ResultInput:
      type: object
      required:
        - value
        - period_start
        - period_end
        - indicator
        - headquarters
      properties:
        value:
          type: number
          format: decimal
        period_start:
          type: string
          format: date
        period_end:
          type: string
          format: date
        notes:
          type: string
        indicator:
          type: integer
        headquarters:
          type: integer

    Process:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        description:
          type: string
        department:
          $ref: '#/components/schemas/Department'
        processType:
          $ref: '#/components/schemas/ProcessType'

    ProcessType:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        description:
          type: string

    Department:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        description:
          type: string
        company:
          $ref: '#/components/schemas/Company'

    Headquarters:
      type: object
      properties:
        id:
          type: integer
          readOnly: true
        name:
          type: string
          maxLength: 255
        address:
          type: string
          maxLength: 255
        phone:
          type: string
          maxLength: 20
        company:
          $ref: '#/components/schemas/Company'

    # =============================================================================
    # ESQUEMAS DE PAGINACIÓN
    # =============================================================================

    PaginatedCompanyList:
      type: object
      properties:
        count:
          type: integer
        next:
          type: string
          format: uri
          nullable: true
        previous:
          type: string
          format: uri
          nullable: true
        results:
          type: array
          items:
            $ref: '#/components/schemas/Company'

    PaginatedFacturaList:
      type: object
      properties:
        count:
          type: integer
        next:
          type: string
          format: uri
          nullable: true
        previous:
          type: string
          format: uri
          nullable: true
        results:
          type: array
          items:
            $ref: '#/components/schemas/Factura'

    PaginatedTerceroList:
      type: object
      properties:
        count:
          type: integer
        next:
          type: string
          format: uri
          nullable: true
        previous:
          type: string
          format: uri
          nullable: true
        results:
          type: array
          items:
            $ref: '#/components/schemas/Tercero'

    PaginatedIndicatorList:
      type: object
      properties:
        count:
          type: integer
        next:
          type: string
          format: uri
          nullable: true
        previous:
          type: string
          format: uri
          nullable: true
        results:
          type: array
          items:
            $ref: '#/components/schemas/Indicator'

    PaginatedResultList:
      type: object
      properties:
        count:
          type: integer
        next:
          type: string
          format: uri
          nullable: true
        previous:
          type: string
          format: uri
          nullable: true
        results:
          type: array
          items:
            $ref: '#/components/schemas/Result'

    # =============================================================================
    # ESQUEMAS DE ERROR
    # =============================================================================

    Error:
      type: object
      properties:
        error:
          type: string
          description: Mensaje de error
        detail:
          type: string
          description: Detalle adicional del error

    ValidationError:
      type: object
      properties:
        field_errors:
          type: object
          additionalProperties:
            type: array
            items:
              type: string
        non_field_errors:
          type: array
          items:
            type: string

  responses:
    # =============================================================================
    # RESPUESTAS REUTILIZABLES
    # =============================================================================

    Unauthorized:
      description: No autenticado
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Credenciales de autenticación no proporcionadas"

    Forbidden:
      description: Sin permisos
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "No tiene permisos para realizar esta acción"

    NotFound:
      description: Recurso no encontrado
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "No encontrado"

    ValidationError:
      description: Error de validación
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidationError'
          example:
            field_errors:
              email: ["Este campo es requerido"]
              password: ["La contraseña es muy corta"]

    ServerError:
      description: Error interno del servidor
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Error interno del servidor"
            detail: "Ha ocurrido un error inesperado"

tags:
  - name: Autenticación
    description: Endpoints relacionados con autenticación y autorización
  - name: Usuarios
    description: Gestión de usuarios y perfiles
  - name: Empresas
    description: Gestión de empresas, departamentos y sedes
  - name: Gestión de Proveedores
    description: Sistema de gestión de proveedores y facturación electrónica
  - name: Terceros
    description: Gestión de terceros, países, departamentos y municipios
  - name: Indicadores
    description: Sistema de indicadores y métricas de gestión
```

---

## 🔧 Configuración de DRF-Spectacular

Para generar automáticamente la documentación OpenAPI en tu proyecto Django, puedes usar DRF-Spectacular:

### Instalación

```bash
pip install drf-spectacular
```

### Configuración en settings.py

```python
INSTALLED_APPS = [
    # ... otras apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Portal Web Backend API',
    'DESCRIPTION': 'Sistema de gestión integral para empresas',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}
```

### URLs

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # ... otras URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

### Personalización de Serializers

```python
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter

@extend_schema_view(
    list=extend_schema(
        summary="Listar facturas",
        description="Obtiene una lista paginada de facturas con filtros opcionales",
        parameters=[
            OpenApiParameter(
                name='etapa',
                description='Filtrar por etapa del proceso',
                required=False,
                type=str,
                enum=['etapa1', 'etapa2', 'etapa3', 'etapa4', 'etapa5', 'etapa6']
            ),
        ]
    ),
    create=extend_schema(
        summary="Crear factura",
        description="Registra una nueva factura en el sistema"
    )
)
class FacturaViewSet(viewsets.ModelViewSet):
    # ... implementación
```

---

## 🌐 Ejemplos de Uso

### Autenticación

```javascript
// 1. Obtener token
const loginResponse = await fetch('/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'admin@example.com',
        password: 'password123'
    })
});

const tokens = await loginResponse.json();

// 2. Usar token en requests
const response = await fetch('/api/gestionProveedores/facturas/', {
    headers: {
        'Authorization': `Bearer ${tokens.access}`,
        'Content-Type': 'application/json'
    }
});
```

### Crear Factura con Archivo

```javascript
const formData = new FormData();
formData.append('factura_fecha', '2024-10-07');
formData.append('factura_valor', '1500000.00');
formData.append('factura_concepto', 'Servicios de consultoría');
formData.append('archivo_factura', fileInput.files[0]);

const response = await fetch('/api/gestionProveedores/facturas/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    },
    body: formData
});
```

### Filtrar Facturas por Etapa

```javascript
const response = await fetch('/api/gestionProveedores/facturas/?etapa=etapa2&page=1', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const facturas = await response.json();
```

---

## 📝 Notas de Implementación

### Rate Limiting
Se recomienda implementar rate limiting para proteger la API:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### Versionado de API
Para futuras versiones:

```python
urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    path('api/v2/', include('api.v2.urls')),
]
```

### Monitoreo
Agregar headers de correlación:

```python
class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.META.get('HTTP_X_CORRELATION_ID') or str(uuid.uuid4())
        request.correlation_id = correlation_id
        response = self.get_response(request)
        response['X-Correlation-ID'] = correlation_id
        return response
```

---

*Documentación generada automáticamente - Versión 1.0.0*