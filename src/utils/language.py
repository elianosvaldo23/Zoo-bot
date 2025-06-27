
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
            'welcome_menu': '🎉 Welcome to Zoo Bot!\n\n🏰 Build your virtual zoo\n⭐ Collect stars from your animals\n💰 Earn money and convert to USDT\n🎮 Play games and win prizes\n👥 Invite friends and earn bonuses\n\nChoose an option from the menu below:',
            'language_selected': '✅ Language set to English',
            'main_menu': '🏠 Main Menu',
            'settings': '⚙️ Settings',
            'settings_menu': '⚙️ Settings Menu\n\nCustomize your preferences:',
            'change_language': '🌐 Change Language',
            'withdrawal_address': '📝 Set Withdrawal Address',
            'view_deposits': '💳 View Deposits',
            'view_withdrawals': '💸 View Withdrawals',
            'view_stats': '📊 View Statistics',
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
            'no_referrals': '👥 You have no referrals yet. Share your link to invite friends!',
            'referral_list_header': '👥 Your Referrals:',
            'earnings_header': '💰 Total Earnings: {total} USDT',
            'no_earnings': '📊 No earnings yet. Invite friends to start earning!',
            'shop_categories': '🏪 Shop Categories',
            'shop_item': '🏷️ {name}\n💰 Price: {price}\n⭐ Stars/hour: {stars}',
            'insufficient_diamonds': '❌ Not enough diamonds!',
            'purchase_success': '✅ Successfully purchased {name}!',
            'shop_menu': '💎 Animal Shop\n\nChoose category:',
            'diamond_packages': '💎 Diamond Packages\n\nSelect a package to purchase:',
            'diamond_purchase_success': '✅ Successfully purchased {amount} diamonds!',
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
            'no_withdrawal_address': '❌ No withdrawal address set! Please set your withdrawal address first.',
            'enter_withdrawal_address': '📝 Please enter your withdrawal address:',
            'withdrawal_address_set': '✅ Withdrawal address has been set!',
            'insufficient_withdrawal': '❌ Minimum withdrawal amount is {min_amount} USDT. Your balance is too low.',
            'withdrawal_submitted': '✅ Your withdrawal request for {amount} USDT has been submitted!',
            'no_deposits': '💳 You have no deposit history.',
            'deposits_header': '💳 Your Deposit History:',
            'no_withdrawals': '💸 You have no withdrawal history.',
            'withdrawals_header': '💸 Your Withdrawal History:',
            'user_stats': '📊 Your Statistics:\n\n📅 Joined: {join_date}\n🦁 Total Animals: {total_animals}\n👥 Total Referrals: {total_referrals}\n💰 Total Earnings: {total_earnings} USDT',
            'set_withdrawal_address': '📝 Set Withdrawal Address',
        }
        
        # Spanish
        self.languages['es'] = {
            'welcome': '🎉 ¡Bienvenido a Zoo Bot!\n\nElige tu idioma / Choose your language / Escolha seu idioma:',
            'welcome_menu': '🎉 ¡Bienvenido a Zoo Bot!\n\n🏰 Construye tu zoo virtual\n⭐ Recolecta estrellas de tus animales\n💰 Gana dinero y conviértelo a USDT\n🎮 Juega y gana premios\n👥 Invita amigos y gana bonos\n\nElige una opción del menú:',
            'language_selected': '✅ Idioma establecido en Español',
            'main_menu': '🏠 Menú Principal',
            'settings': '⚙️ Ajustes',
            'settings_menu': '⚙️ Menú de Ajustes\n\nPersonaliza tus preferencias:',
            'change_language': '🌐 Cambiar Idioma',
            'withdrawal_address': '📝 Configurar Dirección de Retiro',
            'view_deposits': '💳 Ver Depósitos',
            'view_withdrawals': '💸 Ver Retiros',
            'view_stats': '📊 Ver Estadísticas',
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
            'diamond_packages': '💎 Paquetes de Diamantes\n\nSelecciona un paquete para comprar:',
            'diamond_purchase_success': '✅ ¡Has comprado {amount} diamantes!',
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
            'no_withdrawal_address': '❌ ¡No hay dirección de retiro configurada! Por favor, configura tu dirección primero.',
            'enter_withdrawal_address': '📝 Por favor, ingresa tu dirección de retiro:',
            'withdrawal_address_set': '✅ ¡La dirección de retiro ha sido configurada!',
            'insufficient_withdrawal': '❌ El monto mínimo de retiro es {min_amount} USDT. Tu saldo es muy bajo.',
            'withdrawal_submitted': '✅ ¡Tu solicitud de retiro por {amount} USDT ha sido enviada!',
            'no_deposits': '💳 No tienes historial de depósitos.',
            'deposits_header': '💳 Tu Historial de Depósitos:',
            'no_withdrawals': '💸 No tienes historial de retiros.',
            'withdrawals_header': '💸 Tu Historial de Retiros:',
            'user_stats': '📊 Tus Estadísticas:\n\n📅 Te uniste: {join_date}\n🦁 Total de Animales: {total_animals}\n👥 Total de Referidos: {total_referrals}\n💰 Ganancias Totales: {total_earnings} USDT',
            'set_withdrawal_address': '📝 Configurar Dirección de Retiro',
        }
        
        # Portuguese (Brazil)
        self.languages['pt'] = {
            'welcome': '🎉 Bem-vindo ao Zoo Bot!\n\nEscolha seu idioma / Choose your language / Elige tu idioma:',
            'welcome_menu': '🎉 Bem-vindo ao Zoo Bot!\n\n🏰 Construa seu zoológico virtual\n⭐ Colete estrelas dos seus animais\n💰 Ganhe dinheiro e converta para USDT\n🎮 Jogue e ganhe prêmios\n👥 Convide amigos e ganhe bônus\n\nEscolha uma opção do menu:',
            'language_selected': '✅ Idioma definido para Português',
            'main_menu': '🏠 Menu Principal',
            'settings': '⚙️ Configurações',
            'settings_menu': '⚙️ Menu de Configurações\n\nPersonalize suas preferências:',
            'change_language': '🌐 Mudar Idioma',
            'withdrawal_address': '📝 Configurar Endereço de Saque',
            'view_deposits': '💳 Ver Depósitos',
            'view_withdrawals': '💸 Ver Saques',
            'view_stats': '📊 Ver Estatísticas',
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
            'diamond_packages': '💎 Pacotes de Diamantes\n\nSelecione um pacote para comprar:',
            'diamond_purchase_success': '✅ Você comprou {amount} diamantes!',
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
            'no_withdrawal_address': '❌ Nenhum endereço de saque configurado! Por favor, configure seu endereço primeiro.',
            'enter_withdrawal_address': '📝 Por favor, digite seu endereço de saque:',
            'withdrawal_address_set': '✅ Endereço de saque foi configurado!',
            'insufficient_withdrawal': '❌ O valor mínimo para saque é {min_amount} USDT. Seu saldo está muito baixo.',
            'withdrawal_submitted': '✅ Sua solicitação de saque de {amount} USDT foi enviada!',
            'no_deposits': '💳 Você não tem histórico de depósitos.',
            'deposits_header': '💳 Seu Histórico de Depósitos:',
            'no_withdrawals': '💸 Você não tem histórico de saques.',
            'withdrawals_header': '💸 Seu Histórico de Saques:',
            'user_stats': '📊 Suas Estatísticas:\n\n📅 Entrou em: {join_date}\n🦁 Total de Animais: {total_animals}\n👥 Total de Indicações: {total_referrals}\n💰 Ganhos Totais: {total_earnings} USDT',
            'set_withdrawal_address': '📝 Configurar Endereço de Saque',
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
