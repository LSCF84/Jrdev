'use client'; // Directiva de Next.js para indicar que este componente debe ejecutarse en el cliente.

import React, { useState, useEffect } from 'react';

// Constantes de almacenamiento local
const COOKIE_KEY = 'jrdev_cookies_consent';
const ACCEPTED = 'accepted';

// Definición del componente
const CookieConsentBanner: React.FC = () => {
    // Estado para controlar si el banner debe mostrarse
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // La lógica de localStorage debe ejecutarse solo en el navegador (lado del cliente)
        const consent = localStorage.getItem(COOKIE_KEY);
        // Si no hay consentimiento, mostramos el banner
        if (!consent) {
            setIsVisible(true);
        }
    }, []);

    // Maneja la acción de aceptar (guarda en localStorage y oculta el banner)
    const handleAccept = () => {
        if (typeof window !== 'undefined') {
            localStorage.setItem(COOKIE_KEY, ACCEPTED);
            setIsVisible(false);
            console.log("Consentimiento de cookies aceptado.");
            // Aquí iría la lógica para cargar scripts de analítica
        }
    };

    // Maneja la acción de rechazar (guarda en localStorage y oculta el banner)
    const handleReject = () => {
        if (typeof window !== 'undefined') {
            localStorage.setItem(COOKIE_KEY, 'rejected'); // Marcamos como rechazado
            setIsVisible(false);
            console.log("Cookies rechazadas (solo esenciales).");
            // Aquí iría la lógica para NO cargar scripts no esenciales
        }
    };
    
    // Si no es visible, no renderiza nada
    if (!isVisible) {
        return null;
    }

    // El banner se fija en la parte inferior, con la estética oscura y morada de tu web
    return (
        <div 
            // Utilizamos 'fixed' para que se mantenga visible y 'z-50' para asegurar que esté encima de todo
            className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-sm shadow-2xl p-4 sm:p-5 z-50 border-t border-gray-700 transition-all duration-300 ease-in-out"
            role="alert"
        >
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0">
                
                {/* Contenido del Mensaje */}
                <p className="text-sm text-gray-300 leading-relaxed mr-4 text-center md:text-left">
                    Utilizamos cookies propias y de terceros para fines analíticos y de rendimiento. Al hacer clic en "Aceptar Todo", consientes su uso. Consulta nuestra 
                    <a href="/politica-cookies" className="font-semibold text-purple-400 hover:text-purple-300 underline transition duration-150 ml-1">
                        Política de Cookies
                    </a>.
                </p>

                {/* Botones de Acción */}
                <div className="flex flex-shrink-0 space-x-3 w-full md:w-auto justify-center">
                    {/* Botón de Configurar - Estilo secundario */}
                    <button 
                        onClick={handleReject} // Lo usamos para 'Rechazar' o 'Configurar'
                        className="w-1/2 md:w-auto text-center px-4 py-2 text-sm font-medium text-gray-300 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition duration-150 shadow-sm"
                    >
                        Configurar
                    </button>
                    
                    {/* Botón de Aceptar Todo - Estilo Primario (Morado/Índigo) */}
                    <button 
                        onClick={handleAccept} 
                        className="w-1/2 md:w-auto px-4 py-2 text-sm font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 transition duration-150 shadow-lg"
                    >
                        Aceptar Todo
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CookieConsentBanner;
