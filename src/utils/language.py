
# Language system for Zoo Bot
import json
import os

class LanguageManager:
    def __init__(self):
        self.languages = {}
        self.default_language = 'en'
        self.load_languages()
    
    def load_languages(self):
        """Load all language files"""
        # English (default)
        self.languages['en'] = {
            'welcome': '🎉 Welcome to Zoo Bot!\n\nChoose your language / Elige tu idioma / Escolha seu idioma:',
            'language_selected': '✅ Language set to English',
            'main_menu': '🏠 Main Menu',
            'my_zoo': '🏰 My Zoo',
            'collect_stars': '⭐ Collect Stars',
            'balance': '💰 Balance',
            'games': '🎮 Games',
            'referrals': '👥 Referrals',
            'shop': '💎 Shop',
            'admin': '👑 Admin',
            'back': '🔙 Back',
            'convert_stars': '⭐➡️💰 Convert Stars to Money',
            'convert_money': '💰➡️💵 Convert Money to USDT',
            'buy_diamonds': '💎 Buy Diamonds',
            'withdraw': '💸 Withdraw',
            'deposit': '💳 Deposit',
            'your_balance': '💰 Your Balance:\n\n💰 Money: {money}\n⭐ Stars: {stars}\n💎 Diamonds: {diamonds}\n💵 USDT: {usdt}',
            'no_animals': '🏰 Your zoo is empty! Buy some animals from the shop.',
            'animals_list': '🏰 Your Zoo Animals:\n\n{animals}',
            'stars_collected': '⭐ Collected {stars} stars!',
            'no_stars': '⭐ No stars to collect yet.',
            'referral_stats': '👥 Referral Statistics:\n\n🔗 Your referral link: {link}\n👥 Total referrals: {count}\n💰 Earnings: {earnings}',
            'shop_menu': '💎 Animal Shop\n\nChoose category:',
            'common_animals': '🟢 Common Animals',
            'rare_animals': '🟡 Rare Animals',
            'legendary_animals': '🔴 Legendary Animals',
            'conversion_rate': 'Conversion Rate: {rate}',
            'insufficient_balance': '❌ Insufficient balance!',
            'conversion_success': '✅ Converted successfully!',
            'admin_menu': '👑 Admin Panel',
            'admin_deposits': '💳 Manage Deposits',
            'admin_withdrawals': '💸 Manage Withdrawals',
            'admin_users': '👥 User Management',
            'admin_settings': '⚙️ Settings',
            'not_admin': '❌ You are not authorized to use admin commands.',
            'feature_coming_soon': '🚧 This feature is coming soon!',
            'error_occurred': '❌ An error occurred. Please try again.',
        }
        
        # Spanish
        self.languages['es'] = {
            'welcome': '🎉 ¡Bienvenido a Zoo Bot!\n\nElige tu idioma / Choose your language / Escolha seu idioma:',
            'language_selected': '✅ Idioma establecido en Español',
            'main_menu': '🏠 Menú Principal',
            'my_zoo': '🏰 Mi Zoo',
            'collect_stars': '⭐ Recolectar Estrellas',
            'balance': '💰 Balance',
            'games': '🎮 Juegos',
            'referrals': '👥 Referidos',
            'shop': '💎 Tienda',
            'admin': '👑 Admin',
            'back': '🔙 Volver',
            'convert_stars': '⭐➡️💰 Convertir Estrellas a Dinero',
            'convert_money': '💰➡️💵 Convertir Dinero a USDT',
            'buy_diamonds': '💎 Comprar Diamantes',
            'withdraw': '💸 Retirar',
            'deposit': '💳 Depositar',
            'your_balance': '💰 Tu Balance:\n\n💰 Dinero: {money}\n⭐ Estrellas: {stars}\n💎 Diamantes: {diamonds}\n💵 USDT: {usdt}',
            'no_animals': '🏰 ¡Tu zoo está vacío! Compra algunos animales en la tienda.',
            'animals_list': '🏰 Animales de tu Zoo:\n\n{animals}',
            'stars_collected': '⭐ ¡Recolectaste {stars} estrellas!',
            'no_stars': '⭐ No hay estrellas para recolectar aún.',
            'referral_stats': '👥 Estadísticas de Referidos:\n\n🔗 Tu enlace de referido: {link}\n👥 Total referidos: {count}\n💰 Ganancias: {earnings}',
            'shop_menu': '💎 Tienda de Animales\n\nElige categoría:',
            'common_animals': '🟢 Animales Comunes',
            'rare_animals': '🟡 Animales Raros',
            'legendary_animals': '🔴 Animales Legendarios',
            'conversion_rate': 'Tasa de conversión: {rate}',
            'insufficient_balance': '❌ ¡Balance insuficiente!',
            'conversion_success': '✅ ¡Convertido exitosamente!',
            'admin_menu': '👑 Panel de Administración',
            'admin_deposits': '💳 Gestionar Depósitos',
            'admin_withdrawals': '💸 Gestionar Retiros',
            'admin_users': '👥 Gestión de Usuarios',
            'admin_settings': '⚙️ Configuraciones',
            'not_admin': '❌ No tienes autorización para usar comandos de admin.',
            'feature_coming_soon': '🚧 ¡Esta función estará disponible pronto!',
            'error_occurred': '❌ Ocurrió un error. Por favor intenta de nuevo.',
        }
        
        # Portuguese (Brazil)
        self.languages['pt'] = {
            'welcome': '🎉 Bem-vindo ao Zoo Bot!\n\nEscolha seu idioma / Choose your language / Elige tu idioma:',
            'language_selected': '✅ Idioma definido para Português',
            'main_menu': '🏠 Menu Principal',
            'my_zoo': '🏰 Meu Zoo',
            'collect_stars': '⭐ Coletar Estrelas',
            'balance': '💰 Saldo',
            'games': '🎮 Jogos',
            'referrals': '👥 Indicações',
            'shop': '💎 Loja',
            'admin': '👑 Admin',
            'back': '🔙 Voltar',
            'convert_stars': '⭐➡️💰 Converter Estrelas para Dinheiro',
            'convert_money': '💰➡️💵 Converter Dinheiro para USDT',
            'buy_diamonds': '💎 Comprar Diamantes',
            'withdraw': '💸 Sacar',
            'deposit': '💳 Depositar',
            'your_balance': '💰 Seu Saldo:\n\n💰 Dinheiro: {money}\n⭐ Estrelas: {stars}\n💎 Diamantes: {diamonds}\n💵 USDT: {usdt}',
            'no_animals': '🏰 Seu zoo está vazio! Compre alguns animais na loja.',
            'animals_list': '🏰 Animais do seu Zoo:\n\n{animals}',
            'stars_collected': '⭐ Coletou {stars} estrelas!',
            'no_stars': '⭐ Nenhuma estrela para coletar ainda.',
            'referral_stats': '👥 Estatísticas de Indicação:\n\n🔗 Seu link de indicação: {link}\n👥 Total de indicações: {count}\n💰 Ganhos: {earnings}',
            'shop_menu': '💎 Loja de Animais\n\nEscolha a categoria:',
            'common_animals': '🟢 Animais Comuns',
            'rare_animals': '🟡 Animais Raros',
            'legendary_animals': '🔴 Animais Lendários',
            'conversion_rate': 'Taxa de conversão: {rate}',
            'insufficient_balance': '❌ Saldo insuficiente!',
            'conversion_success': '✅ Convertido com sucesso!',
            'admin_menu': '👑 Painel Admin',
            'admin_deposits': '💳 Gerenciar Depósitos',
            'admin_withdrawals': '💸 Gerenciar Saques',
            'admin_users': '👥 Gerenciamento de Usuários',
            'admin_settings': '⚙️ Configurações',
            'not_admin': '❌ Você não tem autorização para usar comandos admin.',
            'feature_coming_soon': '🚧 Este recurso estará disponível em breve!',
            'error_occurred': '❌ Ocorreu um erro. Tente novamente.',
        }
    
    def get_text(self, key, language='en', **kwargs):
        """Get translated text"""
        if language not in self.languages:
            language = self.default_language
        
        text = self.languages[language].get(key, self.languages[self.default_language].get(key, key))
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        return text
    
    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.languages.keys())

# Global language manager instance
lang_manager = LanguageManager()
